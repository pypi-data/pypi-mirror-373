"""
Generic SQL Database Tool - Connect to any SQL database and execute queries.

Supports: PostgreSQL, MySQL, SQLite, SQL Server, Oracle, and more.
"""

import subprocess
import sys
from typing import Dict, Any, List, Optional
from strands import tool
import tempfile
import os
import json


def install_package(package_name: str) -> bool:
    """Install a Python package if not available."""
    try:
        __import__(package_name.replace("-", "_"))
        return True
    except ImportError:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package_name]
            )
            return True
        except subprocess.CalledProcessError:
            return False


@tool
def sql_tool(
    action: str,
    connection_string: Optional[str] = None,
    query: Optional[str] = None,
    database_type: str = "postgresql",
    host: str = "localhost",
    port: Optional[int] = None,
    database: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    table_name: Optional[str] = None,
    limit: int = 100,
    export_format: str = "table",
) -> Dict[str, Any]:
    """Generic SQL database tool for connecting to and querying databases.

    Actions:
        - connect: Test database connection
        - query: Execute SQL query
        - schema: Show database schema/tables
        - describe: Describe table structure
        - export: Export query results to file

    Database Types:
        - postgresql, mysql, sqlite, mssql, oracle, mariadb

    Args:
        action: Action to perform
        connection_string: Full connection string (overrides individual params)
        query: SQL query to execute
        database_type: Type of database
        host: Database host
        port: Database port
        database: Database name
        username: Username
        password: Password
        table_name: Table name for describe action
        limit: Maximum rows to return
        export_format: Export format (table, json, csv, html)

    Returns:
        Dict containing status and response content
    """

    # Install required packages based on database type
    db_packages = {
        "postgresql": "psycopg2-binary",
        "mysql": "PyMySQL",
        "sqlite": "built-in",
        "mssql": "pyodbc",
        "oracle": "cx_Oracle",
        "mariadb": "PyMySQL",
    }

    if database_type != "sqlite":
        package = db_packages.get(database_type, "sqlalchemy")
        if not install_package(package):
            return {
                "status": "error",
                "content": [
                    {"text": f"❌ Failed to install {package} for {database_type}"}
                ],
            }

    # Install SQLAlchemy for universal database support
    if not install_package("sqlalchemy"):
        return {
            "status": "error",
            "content": [{"text": "❌ Failed to install SQLAlchemy"}],
        }

    try:
        import sqlalchemy as sa
        from sqlalchemy import create_engine, text, inspect
        import pandas as pd
    except ImportError as e:
        return {"status": "error", "content": [{"text": f"❌ Import error: {e}"}]}

    # Build connection string if not provided
    if not connection_string:
        if database_type == "sqlite":
            connection_string = f"sqlite:///{database or ':memory:'}"
        else:
            # Set default ports
            default_ports = {
                "postgresql": 5432,
                "mysql": 3306,
                "mariadb": 3306,
                "mssql": 1433,
                "oracle": 1521,
            }

            port = port or default_ports.get(database_type, 5432)

            if database_type == "postgresql":
                connection_string = (
                    f"postgresql://{username}:{password}@{host}:{port}/{database}"
                )
            elif database_type in ["mysql", "mariadb"]:
                connection_string = (
                    f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
                )
            elif database_type == "mssql":
                connection_string = f"mssql+pyodbc://{username}:{password}@{host}:{port}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
            elif database_type == "oracle":
                connection_string = (
                    f"oracle+cx_oracle://{username}:{password}@{host}:{port}/{database}"
                )

    try:
        # Create engine
        engine = create_engine(connection_string)

        if action == "connect":
            # Test connection
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                return {
                    "status": "success",
                    "content": [
                        {
                            "text": f"✅ Connected to {database_type} database successfully"
                        }
                    ],
                }

        elif action == "query":
            if not query:
                return {
                    "status": "error",
                    "content": [{"text": "❌ Query parameter required"}],
                }

            with engine.connect() as conn:
                result = conn.execute(text(query))

                # Handle different query types
                if result.returns_rows:
                    # SELECT query
                    rows = result.fetchmany(limit)
                    columns = list(result.keys())

                    if export_format == "json":
                        data = [dict(zip(columns, row)) for row in rows]
                        formatted_result = json.dumps(data, indent=2, default=str)
                    elif export_format == "csv":
                        df = pd.DataFrame(rows, columns=columns)
                        formatted_result = df.to_csv(index=False)
                    elif export_format == "html":
                        df = pd.DataFrame(rows, columns=columns)
                        formatted_result = df.to_html(index=False)
                    else:
                        # Table format (default)
                        df = pd.DataFrame(rows, columns=columns)
                        formatted_result = df.to_string(index=False)

                    return {
                        "status": "success",
                        "content": [
                            {
                                "text": f"✅ Query executed successfully ({len(rows)} rows):\n\n{formatted_result}"
                            }
                        ],
                    }
                else:
                    # INSERT/UPDATE/DELETE query
                    conn.commit()
                    return {
                        "status": "success",
                        "content": [
                            {
                                "text": f"✅ Query executed successfully (rows affected: {result.rowcount})"
                            }
                        ],
                    }

        elif action == "schema":
            # Show database schema
            inspector = inspect(engine)
            tables = inspector.get_table_names()

            schema_info = f"📊 **Database Schema ({len(tables)} tables):**\n\n"
            for table in tables:
                columns = inspector.get_columns(table)
                schema_info += f"**{table}:**\n"
                for col in columns[:5]:  # Show first 5 columns
                    schema_info += f"  - {col['name']} ({col['type']})\n"
                if len(columns) > 5:
                    schema_info += f"  ... and {len(columns) - 5} more columns\n"
                schema_info += "\n"

            return {"status": "success", "content": [{"text": schema_info}]}

        elif action == "describe":
            if not table_name:
                return {
                    "status": "error",
                    "content": [{"text": "❌ table_name parameter required"}],
                }

            inspector = inspect(engine)
            columns = inspector.get_columns(table_name)

            table_info = f"📋 **Table: {table_name}**\n\n"
            table_info += "| Column | Type | Nullable | Default |\n"
            table_info += "|--------|------|----------|----------|\n"

            for col in columns:
                nullable = "YES" if col.get("nullable", True) else "NO"
                default = col.get("default", "") or ""
                table_info += (
                    f"| {col['name']} | {col['type']} | {nullable} | {default} |\n"
                )

            return {"status": "success", "content": [{"text": table_info}]}

        elif action == "export":
            if not query:
                return {
                    "status": "error",
                    "content": [{"text": "❌ Query parameter required for export"}],
                }

            with engine.connect() as conn:
                df = pd.read_sql(query, conn)

                # Create temp file for export
                with tempfile.NamedTemporaryFile(
                    mode="w", delete=False, suffix=f".{export_format}"
                ) as f:
                    if export_format == "csv":
                        df.to_csv(f.name, index=False)
                    elif export_format == "json":
                        df.to_json(f.name, orient="records", indent=2)
                    elif export_format == "html":
                        df.to_html(f.name, index=False)

                    return {
                        "status": "success",
                        "content": [
                            {"text": f"✅ Exported {len(df)} rows to {f.name}"}
                        ],
                    }

        else:
            return {
                "status": "error",
                "content": [{"text": f"❌ Unknown action: {action}"}],
            }

    except Exception as e:
        return {
            "status": "error",
            "content": [{"text": f"❌ Database error: {str(e)}"}],
        }
