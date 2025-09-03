from typing import Any

from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.db_models import (
    DatabaseCredentials,
    DatabaseHierarchy,
    DatabaseSelection,
    Enum,
    ExecuteSQLInput,
    ExecuteSQLOutput,
    ListDatabasesInput,
    ListDatabasesOutput,
    ListSchemasInput,
    ListSchemasOutput,
    ListTablesInput,
    ListTablesOutput,
    NLToSQLInput,
    NLToSQLOutput,
    SchemaSelection,
    SearchTablesInput,
    SearchTablesOutput,
    SourceSelectionInput,
    SourceSelectionOutput,
    SQADatabaseConfig,
    SqlDialect,
    SqlType,
)

__all__ = [
    "DatabaseCredentials",
    "DatabaseHierarchy",
    "DatabaseSelection",
    "Enum",
    "ExecuteSQLInput",
    "ExecuteSQLOutput",
    "ListDatabasesInput",
    "ListDatabasesOutput",
    "ListSchemasInput",
    "ListSchemasOutput",
    "ListTablesInput",
    "ListTablesOutput",
    "NLToSQLInput",
    "NLToSQLOutput",
    "SQADatabaseConfig",
    "SchemaSelection",
    "SearchTablesInput",
    "SearchTablesOutput",
    "SourceSelectionInput",
    "SourceSelectionOutput",
    "SqlDialect",
    "SqlType",
    "generate_sql",
    "execute_sql",
    "list_databases",
    "list_schemas",
    "list_tables",
    "search_tables",
]


def generate_sql(
    *,
    query: str,
    num_tables_to_filter_for_sql_generation: int = DEFAULT,
    sample_rows: dict[str, list[dict[str, Any]]] | None = DEFAULT,
    connector_name: str,
) -> NLToSQLOutput:
    """
    Convert natural language queries to SQL with automatic table selection.

    This tool combines table selection and SQL generation into a single step:
    1. Analyzes your query to select the most relevant tables
    2. Generates optimized SQL using the selected tables
    3. Converts to the appropriate SQL dialect for your database
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = NLToSQLInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="nl_to_sql", name="generate_sql", input=input_model.model_dump()
    )
    return NLToSQLOutput.model_validate(output_model)


def execute_sql(
    *,
    sql_query: str,
    database_name: str,
    connector_name: str,
    limit: int | None = DEFAULT,
) -> ExecuteSQLOutput:
    """
    Execute a SQL query and return results as a pandas DataFrame-compatible format.

    This tool executes raw SQL queries against your database and returns the results
    in a format that can be easily converted to a pandas DataFrame. It supports all
    standard SQL operations including SELECT, JOIN, GROUP BY, etc.

    The results are returned as a list of dictionaries where each dictionary represents
    a row, making it easy to work with the data in Python.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ExecuteSQLInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="nl_to_sql", name="execute_sql", input=input_model.model_dump()
    )
    return ExecuteSQLOutput.model_validate(output_model)


def list_databases(*, connector_name: str) -> ListDatabasesOutput:
    """
    List all available databases from the specified connector.

    This tool returns a list of all databases accessible through the connector,
    useful for database discovery and exploration.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ListDatabasesInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="nl_to_sql", name="list_databases", input=input_model.model_dump()
    )
    return ListDatabasesOutput.model_validate(output_model)


def list_schemas(*, database_name: str, connector_name: str) -> ListSchemasOutput:
    """
    List all schemas in the specified database.

    This tool returns a list of all schemas within a database, helpful for
    understanding the database structure and organization.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ListSchemasInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="nl_to_sql", name="list_schemas", input=input_model.model_dump()
    )
    return ListSchemasOutput.model_validate(output_model)


def list_tables(
    *, database_name: str, schema_name: str, connector_name: str
) -> ListTablesOutput:
    """
    List all tables in the specified schema of a database.

    This tool returns a list of all tables within a schema, useful for
    exploring the data structure and finding specific tables.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ListTablesInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="nl_to_sql", name="list_tables", input=input_model.model_dump()
    )
    return ListTablesOutput.model_validate(output_model)


def search_tables(
    *, query: str, connector_name: str, num_tables: int = DEFAULT
) -> SearchTablesOutput:
    """
    Search for relevant tables using natural language queries.

    This tool uses semantic search to find tables that match your query,
    returning the most relevant tables with scores and explanations.
    It's particularly useful when you don't know the exact table names
    but know what kind of data you're looking for.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = SearchTablesInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="nl_to_sql", name="search_tables", input=input_model.model_dump()
    )
    return SearchTablesOutput.model_validate(output_model)
