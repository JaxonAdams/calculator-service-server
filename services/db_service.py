import pymysql

from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_DATABASE


class DBService:
    """Service class for interacting with the database."""

    def __init__(self):

        self.host = DB_HOST
        self.port = DB_PORT
        self.user = DB_USER
        self.password = DB_PASSWORD
        self.db = DB_DATABASE

        self.connection = None

    def __enter__(self):
        """Establish a connection to the database when entering a context."""

        self.connect()

        return self

    def __exit__(self, _, __, ___):
        """Close the database connection when exiting a context."""

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

        # Create the SQL query string with placeholders for the data
        columns = ", ".join(f"`{k}`" for k in data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        # Execute the query and commit the transaction
        with self.connection.cursor() as cursor:
            cursor.execute(sql, tuple(data.values()))
            self.connection.commit()

            return cursor.lastrowid

    def update_record(self, table, data, record_id):
        """Update the requested record with the data provided."""

        # Create the SQL query string with placeholders for the data
        set_str = ", ".join(f"{key} = %s" for key in data.keys())
        sql = f"UPDATE {table} SET {set_str} WHERE id = %s"

        params = tuple(data.values()) + (record_id,)

        # Execute the query and commit the transaction
        with self.connection.cursor() as cursor:
            cursor.execute(sql, params)
            self.connection.commit()

            return cursor.lastrowid

    def fetch_records(
        self,
        table,
        fields=["*"],
        join=[],
        conditions=None,
        limit=None,
        offset=None,
        order_by=None,
    ):
        """Fetch records from a specified table with optional conditions."""

        condition_str = ""
        params = []

        # Construct the query string based on the provided parameters
        if conditions:
            condition_str = " WHERE " + " AND ".join(
                f"{k}=%s" for k in conditions.keys()
            )
            params.extend(conditions.values())

        fields_str = ", ".join(f"`{f}`" if f != "*" else f for f in fields)

        join_str = ""
        if len(join):
            for to_join in join:
                join_str += f" JOIN {to_join['table']} ON {to_join['left']} = {to_join['right']}"

        query = f"SELECT {fields_str} FROM {table}{join_str}{condition_str}"

        if order_by:
            query += f" ORDER BY {order_by}"

        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)

        if offset is not None:
            query += " OFFSET %s"
            params.append(offset)

        # Execute the query and return the results
        return self.execute_query(query, tuple(params))

    def count_records(self, table, conditions=None):
        """Count the number of records in the specified table with optional conditions."""
    
        query = f"SELECT COUNT(*) FROM {table}"
        params = []

        if conditions:
            condition_str = " WHERE " + " AND ".join(
                f"{k}=%s" for k in conditions.keys()
            )
            params.extend(conditions.values())

            query += condition_str

        result = self.execute_query(query, tuple(params))
        return result[0]["COUNT(*)"] if result else 0
