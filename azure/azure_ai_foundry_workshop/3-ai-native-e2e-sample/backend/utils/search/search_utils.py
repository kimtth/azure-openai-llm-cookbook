from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex, SimpleField, SearchFieldDataType, SearchableField
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ConnectionType
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def create_literature_index(project_client: AIProjectClient, index_name: str = "literature-index") -> SearchIndex:
    """Create an Azure AI Search index for literature documents.
    
    Args:
        project_client: The AIProjectClient instance
        index_name: Name of the search index to create
        
    Returns:
        The created SearchIndex instance
    """
    try:
        search_conn = project_client.connections.get_default(
            connection_type=ConnectionType.AZURE_AI_SEARCH,
            include_credentials=True
        )
        if not search_conn:
            raise RuntimeError("No default Azure AI Search connection found")
        
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="title", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="abstract", type=SearchFieldDataType.String),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SearchableField(name="authors", type=SearchFieldDataType.Collection(SearchFieldDataType.String)),
            SimpleField(name="publicationDate", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True)
        ]
        
        index = SearchIndex(name=index_name, fields=fields)
        index_client = SearchIndexClient(
            endpoint=search_conn.endpoint_url,
            credential=AzureKeyCredential(search_conn.key)
        )
        
        # Delete existing index if it exists
        if index_name in [x.name for x in index_client.list_indexes()]:
            logger.info(f"Deleting existing index: {index_name}")
            index_client.delete_index(index_name)
        
        created_index = index_client.create_index(index)
        logger.info(f"Created search index: {created_index.name}")
        return created_index
        
    except Exception as e:
        logger.error(f"Failed to create literature index: {str(e)}")
        raise

def upload_literature_docs(
    project_client: AIProjectClient,
    documents: List[Dict[str, Any]],
    index_name: str = "literature-index"
) -> None:
    """Upload documents to the literature search index.
    
    Args:
        project_client: The AIProjectClient instance
        documents: List of documents to upload
        index_name: Name of the search index
    """
    try:
        search_conn = project_client.connections.get_default(
            connection_type=ConnectionType.AZURE_AI_SEARCH,
            include_credentials=True
        )
        if not search_conn:
            raise RuntimeError("No default Azure AI Search connection found")
            
        search_client = SearchClient(
            endpoint=search_conn.endpoint_url,
            index_name=index_name,
            credential=AzureKeyCredential(search_conn.key)
        )
        
        result = search_client.upload_documents(documents=documents)
        logger.info(f"Uploaded {len(documents)} documents to index {index_name}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to upload documents: {str(e)}")
        raise
