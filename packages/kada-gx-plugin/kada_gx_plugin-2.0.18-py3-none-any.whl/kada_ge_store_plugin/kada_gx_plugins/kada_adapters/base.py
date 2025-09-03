import pandas as pd


class KadaAdapterException(Exception):
    """Base exception class for all adapter-related exceptions."""
    pass


class BaseAdapter:
    """
    Base class for all adapters.
    This class defines the interface that all adapters must implement.

    Attributes:
        conn_string: The connection string to be used by the adapter.
    """

    def __init__(self, con: str | dict):
        self.con = con
        self._connection = None

    def connect(self):
        """Establish a connection to the database."""
        raise NotImplementedError("Subclasses must implement this method.")

    def test_connection(self):
        """Test the connection to the database."""
        raise NotImplementedError("Subclasses must implement this method.")

    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a SQL query and return the result as a DataFrame to be passed to BATCH."""
        raise NotImplementedError("Subclasses must implement this method.")
