import os
from typing import Optional

from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool
from google.adk.tools.google_search_tool import GoogleSearchTool


def build_vertex_ai_search_tool(
    data_store_id: Optional[str] = None,
    bypass_multi_tools_limit: bool = True,
) -> VertexAiSearchTool:
    """
    Build a VertexAiSearchTool configured for your Vertex AI Search datastore.

    data_store_id can be:
      projects/<PROJECT_ID>/locations/<REGION>/collections/default_collection/dataStores/<DATASTORE_ID>
    """
    data_store_id = data_store_id or os.getenv("VERTEX_SEARCH_DATA_STORE_ID")

    if not data_store_id:
        raise ValueError(
            "VERTEX_SEARCH_DATA_STORE_ID not set and no data_store_id provided. "
            "Set it to your Vertex AI Search data store path."
        )

    return VertexAiSearchTool(
        data_store_id=data_store_id,
        bypass_multi_tools_limit=bypass_multi_tools_limit,
    )


def build_google_search_tool(
    bypass_multi_tools_limit: bool = True,
) -> GoogleSearchTool:
    """
    Build a GoogleSearchTool for web search.

    Note: Make sure you comply with Google Search grounding UI requirements
    when using this in production. 
    """
    return GoogleSearchTool(bypass_multi_tools_limit=bypass_multi_tools_limit)
