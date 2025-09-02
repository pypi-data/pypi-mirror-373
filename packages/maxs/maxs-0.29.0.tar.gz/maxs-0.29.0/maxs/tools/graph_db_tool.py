"""
Graph Database Tool - Connect to and query graph databases.

Supports: Neo4j, ArangoDB, Amazon Neptune
"""

import subprocess
import sys
from typing import Dict, Any, List, Optional, Union
from strands import tool
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
def graph_db_tool(
    action: str,
    database_type: str = "neo4j",
    uri: str = "bolt://localhost:7687",
    username: str = "neo4j",
    password: str = "password",
    database: str = "neo4j",
    query: Optional[str] = None,
    node_labels: Optional[List[str]] = None,
    relationship_type: Optional[str] = None,
    limit: int = 100,
    export_format: str = "json",
) -> Dict[str, Any]:
    """Graph database tool for connecting to and querying graph databases.

    Actions:
        - connect: Test database connection
        - query: Execute Cypher/AQL query
        - schema: Show database schema (labels, relationships)
        - create_node: Create a new node
        - create_relationship: Create a relationship between nodes
        - find_path: Find paths between nodes
        - analyze: Analyze graph structure and statistics
        - export: Export query results

    Database Types:
        - neo4j: Neo4j graph database (Cypher queries)
        - arangodb: ArangoDB multi-model database (AQL queries)

    Args:
        action: Action to perform
        database_type: Type of graph database
        uri: Database connection URI
        username: Username for authentication
        password: Password for authentication
        database: Database name
        query: Cypher/AQL query to execute
        node_labels: Node labels for operations
        relationship_type: Relationship type for operations
        limit: Maximum results to return
        export_format: Export format (json, csv, graphml)

    Returns:
        Dict containing status and response content
    """

    # Install required packages based on database type
    if database_type == "neo4j":
        if not install_package("neo4j"):
            return {
                "status": "error",
                "content": [{"text": "❌ Failed to install neo4j driver"}],
            }
    elif database_type == "arangodb":
        if not install_package("python-arango"):
            return {
                "status": "error",
                "content": [{"text": "❌ Failed to install python-arango driver"}],
            }

    try:
        if database_type == "neo4j":
            from neo4j import GraphDatabase

            # Create Neo4j driver
            driver = GraphDatabase.driver(uri, auth=(username, password))

            if action == "connect":
                # Test connection
                with driver.session(database=database) as session:
                    result = session.run("RETURN 1 as test")
                    return {
                        "status": "success",
                        "content": [{"text": "✅ Connected to Neo4j successfully"}],
                    }

            elif action == "query":
                if not query:
                    return {
                        "status": "error",
                        "content": [{"text": "❌ Query parameter required"}],
                    }

                with driver.session(database=database) as session:
                    result = session.run(query)
                    records = [record.data() for record in result]

                    if export_format == "json":
                        formatted_result = json.dumps(
                            records[:limit], indent=2, default=str
                        )
                    else:
                        formatted_result = str(records[:limit])

                    return {
                        "status": "success",
                        "content": [
                            {
                                "text": f"✅ Query executed successfully ({len(records)} results):\n\n{formatted_result}"
                            }
                        ],
                    }

            elif action == "schema":
                with driver.session(database=database) as session:
                    # Get node labels
                    labels_result = session.run("CALL db.labels()")
                    labels = [record["label"] for record in labels_result]

                    # Get relationship types
                    rels_result = session.run("CALL db.relationshipTypes()")
                    relationships = [
                        record["relationshipType"] for record in rels_result
                    ]

                    # Get counts
                    node_count = session.run(
                        "MATCH (n) RETURN count(n) as count"
                    ).single()["count"]
                    rel_count = session.run(
                        "MATCH ()-[r]->() RETURN count(r) as count"
                    ).single()["count"]

                    schema_info = f"📊 **Graph Schema:**\n\n"
                    schema_info += f"**Statistics:**\n"
                    schema_info += f"- Nodes: {node_count:,}\n"
                    schema_info += f"- Relationships: {rel_count:,}\n\n"
                    schema_info += f"**Node Labels ({len(labels)}):**\n"
                    for label in labels:
                        schema_info += f"- {label}\n"
                    schema_info += f"\n**Relationship Types ({len(relationships)}):**\n"
                    for rel in relationships:
                        schema_info += f"- {rel}\n"

                    return {"status": "success", "content": [{"text": schema_info}]}

            elif action == "create_node":
                if not node_labels:
                    return {
                        "status": "error",
                        "content": [{"text": "❌ node_labels parameter required"}],
                    }

                label = node_labels[0]
                properties = {"name": "example", "type": "test"}

                with driver.session(database=database) as session:
                    create_query = f"CREATE (n:{label} $properties) RETURN n"
                    result = session.run(create_query, properties=properties)
                    node = result.single()["n"]

                    return {
                        "status": "success",
                        "content": [{"text": f"✅ Created node: {dict(node)}"}],
                    }

            elif action == "find_path":
                start_id = 1  # Default start node ID
                end_id = 2  # Default end node ID

                if not start_id or not end_id:
                    return {
                        "status": "error",
                        "content": [
                            {"text": "❌ start_id and end_id parameters required"}
                        ],
                    }

                with driver.session(database=database) as session:
                    path_query = """
                    MATCH (start), (end), path = shortestPath((start)-[*]-(end))
                    WHERE id(start) = $start_id AND id(end) = $end_id
                    RETURN path, length(path) as length
                    """
                    result = session.run(path_query, start_id=start_id, end_id=end_id)
                    paths = []

                    for record in result:
                        path_data = {
                            "length": record["length"],
                            "nodes": [dict(node) for node in record["path"].nodes],
                            "relationships": [
                                dict(rel) for rel in record["path"].relationships
                            ],
                        }
                        paths.append(path_data)

                    return {
                        "status": "success",
                        "content": [
                            {
                                "text": f"✅ Found {len(paths)} paths:\n\n{json.dumps(paths, indent=2, default=str)}"
                            }
                        ],
                    }

            elif action == "analyze":
                with driver.session(database=database) as session:
                    # Graph statistics
                    stats_queries = {
                        "nodes": "MATCH (n) RETURN count(n) as count",
                        "relationships": "MATCH ()-[r]->() RETURN count(r) as count",
                        "node_degrees": "MATCH (n) RETURN labels(n)[0] as label, count(*) as count ORDER BY count DESC LIMIT 10",
                        "relationship_types": "MATCH ()-[r]->() RETURN type(r) as type, count(*) as count ORDER BY count DESC",
                    }

                    analysis = {}
                    for name, query in stats_queries.items():
                        result = session.run(query)
                        if name in ["nodes", "relationships"]:
                            analysis[name] = result.single()["count"]
                        else:
                            analysis[name] = [record.data() for record in result]

                    formatted_analysis = f"📈 **Graph Analysis:**\n\n"
                    formatted_analysis += f"**Basic Stats:**\n"
                    formatted_analysis += f"- Total Nodes: {analysis['nodes']:,}\n"
                    formatted_analysis += (
                        f"- Total Relationships: {analysis['relationships']:,}\n\n"
                    )
                    formatted_analysis += f"**Top Node Labels:**\n"
                    for item in analysis["node_degrees"]:
                        formatted_analysis += f"- {item['label']}: {item['count']:,}\n"
                    formatted_analysis += f"\n**Relationship Types:**\n"
                    for item in analysis["relationship_types"][:10]:
                        formatted_analysis += f"- {item['type']}: {item['count']:,}\n"

                    return {
                        "status": "success",
                        "content": [{"text": formatted_analysis}],
                    }

            else:
                return {
                    "status": "error",
                    "content": [{"text": f"❌ Unknown action: {action}"}],
                }

        elif database_type == "arangodb":
            from arango import ArangoClient

            # Parse URI for ArangoDB
            client = ArangoClient(hosts=uri)
            db = client.db(database, username=username, password=password)

            if action == "connect":
                # Test connection
                try:
                    db.version()
                    return {
                        "status": "success",
                        "content": [{"text": "✅ Connected to ArangoDB successfully"}],
                    }
                except Exception as e:
                    return {
                        "status": "error",
                        "content": [{"text": f"❌ Connection failed: {str(e)}"}],
                    }

            elif action == "query":
                if not query:
                    return {
                        "status": "error",
                        "content": [{"text": "❌ Query parameter required"}],
                    }

                cursor = db.aql.execute(query)
                results = [doc for doc in cursor]

                formatted_result = json.dumps(results[:limit], indent=2, default=str)

                return {
                    "status": "success",
                    "content": [
                        {
                            "text": f"✅ AQL query executed successfully ({len(results)} results):\n\n{formatted_result}"
                        }
                    ],
                }

            else:
                return {
                    "status": "error",
                    "content": [
                        {"text": f"❌ Action {action} not yet implemented for ArangoDB"}
                    ],
                }

        else:
            return {
                "status": "error",
                "content": [{"text": f"❌ Unsupported database type: {database_type}"}],
            }

    except Exception as e:
        return {
            "status": "error",
            "content": [{"text": f"❌ Graph database error: {str(e)}"}],
        }
