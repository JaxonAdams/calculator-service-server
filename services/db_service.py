import pymysql

from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_DATABASE


class DBService:

    def __init__(self):
        
        self.host = DB_HOST
        self.port = DB_PORT
        self.user = DB_USER
        self.password = DB_PASSWORD
        self.db = DB_DATABASE
        
        self.connection = None

    def __enter__(self):

        self.connect()

        return self

    def __exit__(self, _, __, ___):

        self.close_connection()

    def connect(self):
        """Establish a connection to the database."""

        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.db,
                cursorclass=pymysql.cursors.DictCursor,
            )
        except pymysql.MySQLError as e:
            print(f"Error connecting to the database: {e}")
            self.connection = None

    def close_connection(self):
        """Close the database connection."""

        if self.connection:
            self.connection.close()
