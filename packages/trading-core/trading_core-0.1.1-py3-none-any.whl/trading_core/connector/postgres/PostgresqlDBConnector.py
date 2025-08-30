import psycopg2
import logging

logger = logging.getLogger(__name__)

class PostgresqlDBConnector:
    _instances = {}

    def __new__(cls, db_name, db_port, db_host, db_user, db_password):
        config_key = (db_name, db_port, db_host, db_user, db_password)

        if config_key not in cls._instances:
            instance = super(PostgresqlDBConnector, cls).__new__(cls)
            cls._instances[config_key] = instance
            instance.__init__(db_name, db_port, db_host, db_user, db_password)
        
        return cls._instances[config_key]

    def __init__(self, db_name, db_port, db_host, db_user, db_password):
        self.db_name = db_name
        self.db_port = db_port
        self.db_host = db_host
        self.db_user = db_user
        self.db_password = db_password
        self.connection = None
        self.cursor = None

    def connect(self):
        if self.connection:
            logger.info("Reusing existing connection")
            return self.connection
        try:
            self.connection = psycopg2.connect(
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port
            )
            self.cursor = self.connection.cursor()
            logger.info("Connected to PostgreSQL")
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise

    def execute_query(self, query, params=None):
        if not self.connection:
            self.connect()
        self.cursor.execute(query, params)
        self.connection.commit()
        return self.cursor

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Connection closed")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
