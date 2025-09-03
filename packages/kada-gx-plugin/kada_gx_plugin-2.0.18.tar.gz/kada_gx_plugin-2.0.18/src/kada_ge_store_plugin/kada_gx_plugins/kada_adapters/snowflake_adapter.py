import pandas as pd
import snowflake.connector
from typing import Sequence

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


from .base import BaseAdapter, KadaAdapterException
from .utils import resolve_conn_params


class SnowflakeAdapter(BaseAdapter):
    """
    Snowflake adapter for connecting to Snowflake databases.
    This adapter supports connecting to Snowflake using a private key
    """
    required_conn_params = [
        'user',
        'account',
        'database',
        'key',
        'warehouse',
        'role',
        'passphrase'
    ]

    def connect(self):
        """
        Establish a connection to Snowflake using private key authentication.

        If self.con is a string, it will be resolved to get the connection parameters
        and extract params from environment variables if needed. Otherwise, if it is a dict,
        it will be used directly as the connection parameters.

        Returns:
            A Snowflake connection object.

        Raises:
            KadaAdapterException: If connection fails or required parameters are missing.
        """
        if self._connection:
            return self._connection

        try:
            if isinstance(self.con, str):
                # If the connection string is a string, resolve it to get the parameters
                params = resolve_conn_params(
                    conn_string=self.con,
                    scheme='snowflake',
                )
            elif isinstance(self.con, dict):
                params = self.con.copy()

            missing_params = [param for param in self.required_conn_params if param not in params]
            if missing_params:
                raise KadaAdapterException(
                    f"Missing required connection parameters: {', '.join(missing_params)}"
                )

            connection_args = {}

            private_key = params.pop('key').replace('\\n', '\n')
            passphrase = params.pop('passphrase', None)
            p_key = serialization.load_pem_private_key(
                private_key.encode(),
                password=passphrase.encode() if passphrase else None,
                backend=default_backend()
            )
            connection_args['private_key'] = p_key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            connection_args.update(params)
            self._connection = snowflake.connector.connect(**connection_args)
            return self._connection
        except Exception as e:
            raise KadaAdapterException(f"Failed to connect to Snowflake: {str(e)}")

    def test_connection(self):
        """
        Test the connection to Snowflake.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        try:
            with self.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    return True
        except Exception as e:
            raise KadaAdapterException(f"Connection test failed: {str(e)}")

    def execute_query(
        self,
        query: str,
        index_col: str | Sequence[str] | None = None
    ) -> pd.DataFrame:
        """
        Execute a SQL query and return the result as a DataFrame.

        Attributes:
            query (str): The SQL query to be executed

        Returns:
            pd.DataFrame: The result of the query as a DataFrame.
        """
        try:
            with self.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    column_names = [desc[0] for desc in cur.description]
                    df = pd.DataFrame(cur, columns=column_names)
                    if index_col:
                        df = df.set_index(index_col)

                    return df
        except Exception as e:
            raise KadaAdapterException(f"Query execution failed: {str(e)}")
