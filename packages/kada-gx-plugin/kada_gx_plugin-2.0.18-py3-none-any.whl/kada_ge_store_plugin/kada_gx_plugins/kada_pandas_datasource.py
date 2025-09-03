from typing import Literal

from great_expectations.datasource.fluent import PandasDatasource

from .kada_sql_query_asset import KadaSQLQueryAsset


class KadaPandasDatasource(PandasDatasource):
    """
    Kada Custom Pandas Datasource.
    It inherits from the PandasDatasource class to override 
    add_sql_query_asset method to use KadaSQLQueryAsset custom asset,
    which utilizes a custom ConnectionAdapter to connect to the database,

    https://github.com/great-expectations/great_expectations/blob/af0c608d2fda9d2604b581e5b61459a41a83de7d/great_expectations/datasource/fluent/pandas_datasource.py#L623
    """
    # Extend the asset types to include the custom SQL query asset
    asset_types = PandasDatasource.asset_types + [KadaSQLQueryAsset]

    type: Literal["kada_pandas"] = "kada_pandas"

    def add_sql_query_asset(
        self,
        name: str,
        sql: str,
        con: str | dict,
        connection_type: str,
        **kwargs
    ) -> KadaSQLQueryAsset:
        """
        Add a SQL query asset that uses a custom adapter to connect to the data source.

        Args:
            name: The name of the asset
            sql: The SQL query to execute
            con: The connection string or dictionary containing connection parameters
            connection_type: The type of adapter to use (e.g. 'snowflake')
            **kwargs: Additional keyword arguments including batch_metadata, index_col, etc.

        Returns:
            KadaSQLQueryAsset: The created SQL query asset
        """
        asset = KadaSQLQueryAsset(
            name=name,
            sql=sql,
            con=con,
            connection_type=connection_type,
            **kwargs
        )
        return self._add_asset(asset=asset)
