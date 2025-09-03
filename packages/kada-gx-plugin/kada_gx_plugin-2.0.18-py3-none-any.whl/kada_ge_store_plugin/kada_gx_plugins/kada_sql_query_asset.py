from typing import Literal, Sequence

from great_expectations.datasource.fluent.interfaces import Batch
from great_expectations.datasource.fluent.pandas_datasource import _PandasDataAsset
from great_expectations.datasource.fluent import BatchRequest
from great_expectations.core.batch import LegacyBatchDefinition
from great_expectations.core.batch_spec import RuntimeDataBatchSpec
from great_expectations.datasource.fluent.constants import _DATA_CONNECTOR_NAME
from great_expectations.datasource.fluent.batch_identifier_util import make_batch_identifier


class KadaSQLQueryAsset(_PandasDataAsset):
    """
    Kada Custom SQL Query Asset.
    It inherits from the _PandasDataAsset class and implements
    to use a custom ConnectionAdapter to connect to the database,
    and bypass GX sqlalchemy engine.

    https://github.com/great-expectations/great_expectations/blob/af0c608d2fda9d2604b581e5b61459a41a83de7d/great_expectations/datasource/fluent/pandas_datasource.py#L87

    Attributes:
        sql: The SQL query to be executed against the database.
        con: The connection string to the database.
        connection_type: The type of connection (e.g., "snowflake")
        index_col: The column(s) to set as the index.

    """
    type: Literal["kada_sql_query"] = "kada_sql_query"

    # Required fields for the asset
    sql: str
    con: str | dict
    connection_type: str
    index_col: str | Sequence[str] | None = None

    def _get_adapter(self):
        """
        Returns the adapter instance based on the connection type and connection string.
        """
        from kada_ge_store_plugin.kada_gx_plugins.kada_adapters.utils import get_adapter
        return get_adapter(connection_type=self.connection_type, con=self.con)

    def _get_reader_method(self) -> str:
        """Not implemented for custom SQL queries."""
        raise NotImplementedError(
            "KadaSQLQueryAsset does not implement '_get_reader_method()' method."
        )

    def _get_reader_options_include(self) -> set[str]:
        """Not implemented for custom SQL queries."""
        raise NotImplementedError(
            "KadaSQLQueryAsset does not implement '_get_reader_options_include()' method."
        )

    def get_batch(self, batch_request: BatchRequest) -> Batch:
        """Retrieves a batch of data by executing the SQL query."""
        self._validate_batch_request(batch_request)

        # Execute the query using the appropriate adapter
        adapter = self._get_adapter()
        df = adapter.execute_query(self.sql, self.index_col)

        # Create a batch specification for the runtime data
        batch_spec = RuntimeDataBatchSpec(batch_data=df)
        execution_engine = self.datasource.get_execution_engine()
        data, markers = execution_engine.get_batch_data_and_markers(batch_spec=batch_spec)

        # Create a legacy batch definition
        batch_definition = LegacyBatchDefinition(
            datasource_name=self.datasource.name,
            data_connector_name=_DATA_CONNECTOR_NAME,
            data_asset_name=self.name,
            batch_identifiers=make_batch_identifier(batch_request.options),
            batch_spec_passthrough=None,
        )

        # Generate batch metadata
        batch_metadata = self._get_batch_metadata_from_batch_request(
            batch_request=batch_request, ignore_options=("dataframe",)
        )

        # Return the batch object
        return Batch(
            datasource=self.datasource,
            data_asset=self,
            batch_request=batch_request,
            data=data,
            metadata=batch_metadata,
            batch_markers=markers,
            batch_spec=batch_spec,
            batch_definition=batch_definition,
        )
