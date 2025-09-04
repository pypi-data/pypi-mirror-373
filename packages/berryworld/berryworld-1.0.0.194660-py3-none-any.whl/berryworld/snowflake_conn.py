import os
import pandas as pd
import snowflake.connector


class SnowflakeConn:
    def __init__(self, db_reference, server=None):
        """ Initialize the class
        :param db_reference: Reference name for the DB to be used
        :param server: Dictionary containing the info to connect to the Server
        """

        self.conn_str = None
        self.conn = None
        self.db_reference = db_reference
        self.server = server

        try:
            snowflake_ref = os.environ.get("SNOWFLAKE-" + self.db_reference.upper() + '-' + self.server.upper())
        except Exception:
            raise Exception(f"Snowflake reference {self.db_reference} not found in the environment variables")

        try:
            self.account = snowflake_ref.split(' ')[0]
        except Exception:
            raise Exception(f"Snowflake account not provided for Reference {self.db_reference}")

        try:
            self.db_name = snowflake_ref.split(' ')[1]
        except Exception:
            raise Exception(f"Snowflake db name not provided for Reference {self.db_reference}")

        try:
            self.user_name = snowflake_ref.split(' ')[2]
        except Exception:
            raise Exception(f"Snowflake username not provided for Reference {self.db_reference}")

        try:
            self.pw = snowflake_ref.split(' ')[3]
        except Exception:
            raise Exception(f"Snowflake password not provided for Reference {self.db_reference}")

        self.connect()

    def connect(self):
        """ Open the connection to Snowflake """
        self.conn = snowflake.connector.connect(
            user=self.user_name,
            password=self.pw,
            account=self.account,
            database=self.db_name)

    def close(self):
        """ Close the connection to Snowflake """
        self.conn.close()

    def query(self, sql_query):
        """ Read data from Snowflake according to the sql_query
        -----------------------------
        query_str = "SELECT * FROM %s" & table
        con_.query(query_str)
        -----------------------------
        :param sql_query: Query to be sent to Snowflake
        :return: DataFrame gathering the requested data
        """
        cursor = None
        self.connect()
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            col_names = [desc[0] for desc in cursor.description]
            result = pd.DataFrame(rows, columns=col_names)
            return result
        except Exception as e:
            raise Exception(e)
        finally:
            if cursor:
                cursor.close()
            self.close()
