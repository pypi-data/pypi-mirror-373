import os
import re
from urllib.parse import parse_qs, urlsplit

from .base import KadaAdapterException


# Pattern for identifying placeholders in connection strings
PLACEHOLDER_PATTERN = re.compile(r'\${([^\}]*)}')


def get_adapter(connection_type: str, con: str) -> str:
    """
    Retrieve and initialize the appropriate adapter based on the connection type.

    Attributes:
        connection_type (str): The type of connection (e.g., 'snowflake').
        conn_string (str): The connection string to be used by the adapter.

    Returns:
        Adapter: An instance of the appropriate adapter class.

    Raises:
        ValueError: If the connection type is not supported.
    """
    if connection_type.lower() == "snowflake":
        from .snowflake_adapter import SnowflakeAdapter
        return SnowflakeAdapter(con)
    # Add other adapters here as needed
    else:
        raise KadaAdapterException(
            f"Unsupported connection type: {connection_type}"
        )


def _resolve_placeholder(value: str) -> str:
    """
    Resolve environment variable placeholders in a string.

    Args:
        value (str): The value that may contain placeholders like ${VAR_NAME}.

    Returns:
        str: The resolved value with placeholders replaced by environment variables.
    """
    placeholders = PLACEHOLDER_PATTERN.findall(value)

    if not placeholders:
        return value

    result = value
    for placeholder in placeholders:
        env_value = os.environ.get(placeholder)
        if env_value is not None:
            result = result.replace(f"${{{placeholder}}}", env_value)

    return result


def resolve_conn_params(conn_string: str, scheme: str) -> dict:
    """
    Resolve the connection parameters from the connection string.

    Attributes:
        conn_string (str): The connection string to be resolved.
        scheme (str): The scheme of the connection string (e.g., 'snowflake').
        required_params (list[str] | None): List of required parameters.

    Returns:
        dict: A dictionary containing the resolved connection parameters.

    Raises:
        KadaAdapterException: If required parameters are missing or invalid format.
    """
    if not conn_string or not isinstance(conn_string, str):
        raise KadaAdapterException(
            "Invalid connection string. It should be a non-empty string."
        )

    if not conn_string.startswith(f"{scheme}://"):
        raise KadaAdapterException(
            f"Invalid connection string format. Expected format should start with: {scheme}://"
        )

    url_parts = urlsplit(conn_string)
    params = {}

    netloc = url_parts.netloc
    if '@' in netloc:
        userinfo, hostname = netloc.split('@', 1)
        if ':' in userinfo:
            username, password = userinfo.split(':', 1)
            params["user"] = _resolve_placeholder(username)
            params["password"] = _resolve_placeholder(password)
        else:
            params["user"] = _resolve_placeholder(userinfo)
        params["account"] = _resolve_placeholder(hostname)
    else:
        params["account"] = _resolve_placeholder(netloc)

    if url_parts.path and url_parts.path != '/':
        params["database"] = _resolve_placeholder(url_parts.path.lstrip('/'))

    query_params = parse_qs(url_parts.query)
    for key, values in query_params.items():
        if values:
            params[key] = _resolve_placeholder(values[0])

    return params
