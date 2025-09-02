"""CodeMie MCP implementation for datasources."""

import os
import sys
from typing import Any, Dict, List, Optional, Literal

from codemie_sdk import CodeMieClient
from codemie_sdk.models.datasource import (
    DataSourceType,
    DataSourceStatus,
    CodeDataSourceRequest,
    UpdateCodeDataSourceRequest,
)
from mcp.server.fastmcp import FastMCP

DEFAULT_AUTH_CLIENT_ID = "codemie-sdk"
DEFAULT_AUTH_REALM_NAME = "codemie-prod"
DEFAULT_AUTH_SERVER_URL = (
    "https://keycloak.eks-core.aws.main.edp.projects.epam.com/auth"
)
DEFAULT_CODEMIE_API_DOMAIN = "https://codemie.lab.epam.com/code-assistant-api"

# Initialize FastMCP server
mcp = FastMCP("codemie-datasources")

# Client instance
_client: Optional[CodeMieClient] = None


def get_client() -> CodeMieClient:
    """Gets authenticated CodeMie client instance."""
    username = os.getenv("CODEMIE_USERNAME")
    password = os.getenv("CODEMIE_PASSWORD")
    auth_client_id = os.getenv("CODEMIE_AUTH_CLIENT_ID", DEFAULT_AUTH_CLIENT_ID)
    auth_realm_name = os.getenv("CODEMIE_AUTH_REALM_NAME", DEFAULT_AUTH_REALM_NAME)
    auth_server_url = os.getenv("CODEMIE_AUTH_SERVER_URL", DEFAULT_AUTH_SERVER_URL)
    codemie_api_domain = os.getenv("CODEMIE_API_DOMAIN", DEFAULT_CODEMIE_API_DOMAIN)

    if not username or not password:
        raise ValueError(
            "Username and password must be set via environment variables: CODEMIE_USERNAME, CODEMIE_PASSWORD"
        )

    return CodeMieClient(
        username=username,
        password=password,
        verify_ssl=False,
        auth_client_id=auth_client_id,
        auth_realm_name=auth_realm_name,
        auth_server_url=auth_server_url,
        codemie_api_domain=codemie_api_domain,
    )


@mcp.tool()
async def list_datasources(
    page: int = 0,
    per_page: int = 10,
    sort_key: Literal["date", "update_date"] = "update_date",
    sort_order: Literal["asc", "desc"] = "desc",
    datasource_types: List[DataSourceType] = None,
    projects: List[str] = None,
    owner: str = None,
    status: DataSourceStatus = None,
) -> List[Dict[str, Any]]:
    """Get list of available datasources.

    Args:
        sort_key: sort results by params
        sort_order: sort results in order
        page: Page number (default: 0)
        per_page: Items per page (default: 10)
        projects: Filter by project name
        datasource_types: Filter by datasource type
        owner: Filter by owner
        status: Filter by status
    """
    client = get_client()

    datasources = client.datasources.list(
        page=page,
        per_page=per_page,
        sort_key=sort_key,
        sort_order=sort_order,
        datasource_types=datasource_types,
        projects=projects,
        owner=owner,
        status=status,
    )

    # Convert to simplified dict format
    return [
        {
            "id": ds.id,
            "name": ds.name,
            "description": ds.description,
            "type": ds.type.value,
            "project": ds.project_name,
            "status": ds.status.value,
            "created_date": ds.created_date.isoformat() if ds.created_date else None,
            "update_date": ds.update_date.isoformat() if ds.update_date else None,
            "error_message": ds.error_message,
            "processing_info": ds.processing_info.model_dump()
            if ds.processing_info
            else None,
        }
        for ds in datasources
    ]


@mcp.tool()
async def get_datasource(datasource_id: str) -> Dict[str, Any]:
    """Get datasource details by ID.

    Args:
        datasource_id: ID of the datasource to retrieve
    """
    client = get_client()
    datasource = client.datasources.get(datasource_id)

    return {
        "id": datasource.id,
        "name": datasource.name,
        "description": datasource.description,
        "type": datasource.type.value,
        "project": datasource.project_name,
        "status": datasource.status.value,
        "created_date": datasource.created_date.isoformat()
        if datasource.created_date
        else None,
        "update_date": datasource.update_date.isoformat()
        if datasource.update_date
        else None,
        "error_message": datasource.error_message,
        "processing_info": datasource.processing_info.model_dump()
        if datasource.processing_info
        else None,
        "code": datasource.code.model_dump() if datasource.code else None,
        "jira": datasource.jira.model_dump() if datasource.jira else None,
        "confluence": datasource.confluence.model_dump()
        if datasource.confluence
        else None,
    }


@mcp.tool()
async def create_code_datasource(
    name: str,
    description: str,
    project_name: str,
    repository_link: str,
    branch: str,
    index_type: str = "code",
    files_filter: str = "",
    embeddings_model: Optional[str] = None,
    shared_with_project: bool = False,
) -> Dict[str, Any]:
    """Create a new code datasource.

    Args:
        name: Datasource name (lowercase letters and underscores only)
        description: Datasource description
        project_name: Project name
        repository_link: Git repository URL
        branch: Git branch name
        index_type: Type of indexing (code, summary, chunk-summary)
        files_filter: File patterns to include/exclude
        embeddings_model: Model for embeddings generation
        shared_with_project: Whether datasource is shared with project
    """
    client = get_client()

    request = CodeDataSourceRequest(
        name=name,
        description=description,
        project_name=project_name,
        link=repository_link,
        branch=branch,
        index_type=index_type,
        files_filter=files_filter,
        embeddings_model=embeddings_model,
        shared_with_project=shared_with_project,
    )

    datasource = client.datasources.create(request)
    return get_datasource(datasource.id)


@mcp.tool()
async def delete_datasource(datasource_id: str) -> Dict[str, Any]:
    """Delete a datasource.

    Args:
        datasource_id: ID of the datasource to delete
    """
    client = get_client()
    return client.datasources.delete(datasource_id)


@mcp.tool()
async def update_code_datasource(
    datasource_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    branch: Optional[str] = None,
    files_filter: Optional[str] = None,
    full_reindex: Optional[bool] = None,
    skip_reindex: Optional[bool] = None,
    resume_indexing: Optional[bool] = None,
) -> Dict[str, Any]:
    """Update a code datasource.

    Args:
        datasource_id: ID of the datasource to update
        name: New name (optional)
        description: New description (optional)
        branch: New branch (optional)
        files_filter: New files filter (optional)
        full_reindex: Whether to perform full reindex
        skip_reindex: Whether to skip reindex
        resume_indexing: Whether to resume indexing
    """
    client = get_client()

    # First get current datasource
    current = client.datasources.get(datasource_id)

    # Prepare update request
    request = UpdateCodeDataSourceRequest(
        name=name or current.name,
        description=description or current.description,
        project_name=current.project_name,
        branch=branch or current.code.branch if current.code else None,
        files_filter=files_filter or current.code.files_filter
        if current.code
        else None,
        full_reindex=full_reindex,
        skip_reindex=skip_reindex,
        resume_indexing=resume_indexing,
    )

    datasource = client.datasources.update(datasource_id, request)
    return get_datasource(datasource.id)


@mcp.tool()
async def get_datasource_processing_info(datasource_id: str) -> Dict[str, Any]:
    """Get datasource processing information.

    Args:
        datasource_id: ID of the datasource to get info for
    """
    client = get_client()
    info = client.datasources.get_processing_info(datasource_id)
    return {
        "status": info.status.value if info.status else None,
        "total_files": info.total_files,
        "processed_files": info.processed_files,
        "progress": info.progress,
        "error_message": info.error_message,
    }


def main():
    try:
        print("Starting CodeMie Datasources MCP server", file=sys.stdout)
        # Initialize and run the server
        mcp.run(transport="stdio")
    except Exception as e:
        print(f"Error starting MCP server: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
