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

    def execute_query(self, query, params=None):
        """Execute a query and return the results."""

        if not self.connection:
            print("No database connection")
            return

        with self.connection.cursor() as cursor:
            try:
                cursor.execute(query, params)
                self.connection.commit()
                result = cursor.fetchall()
                return result
            except pymysql.MySQLError as e:
                print(f"Error executing query: {e}")
                return

    def insert_record(self, table, data):
        """Insert a record into the given table with the data provided."""

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        with self.connection.cursor() as cursor:
            cursor.execute(sql, tuple(data.values()))
            self.connection.commit()

            return cursor.lastrowid

    def fetch_records(self, table, conditions=None):
        """Fetch records from a specified table with optional conditions."""

        condition_str = ""
        params = tuple()

        if conditions:
            condition_str = " WHERE " + " AND ".join(
                f"{k}=%s" for k in conditions.keys()
            )
            params = tuple(conditions.values())

        query = f"SELECT * FROM {table}{condition_str}"

        return self.execute_query(query, params)
