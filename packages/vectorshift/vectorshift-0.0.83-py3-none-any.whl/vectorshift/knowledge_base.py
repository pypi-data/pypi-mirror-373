import base64
import mimetypes
import os
from typing import Optional

from pydantic import BaseModel

from vectorshift.request import request_client, async_request_client

class SearchMetadata(BaseModel):
    filter: Optional[str] = None
    opensearch_filter: Optional[str] = None
    group_by_key: Optional[str] = None
    top_k: int = 5

class RetrievalConfig(BaseModel):
    max_documents: int = 5
    data_fusion_method: Optional[str] = None

class RerankingConfig(BaseModel):
    reranking_model: Optional[str] = None
    api_key: Optional[str] = None
    num_chunks_to_rerank: Optional[int] = None

class QuestionAnsweringConfig(BaseModel):
    qa_model: Optional[str] = None
    advanced_qa_mode: Optional[str] = None

class HybridSearchConfig(BaseModel):
    alpha: Optional[float] = None
    fusion_method: Optional[str] = None

class QueryConfig(BaseModel):
    rerank_documents: Optional[bool] = None
    generate_metadata_filters: Optional[bool] = None
    transform_query: Optional[bool] = None
    answer_multi_query: Optional[bool] = None
    expand_query: Optional[bool] = None
    do_advanced_qa: Optional[bool] = None
    format_context_for_llm: Optional[bool] = None
    generate_ai_doc_summaries: Optional[bool] = None
    retrieval_unit: Optional[str] = None
    score_cutoff: Optional[float] = None
    retrieval_config: Optional[RetrievalConfig] = None
    reranking_config: Optional[RerankingConfig] = None
    question_answering_config: Optional[QuestionAnsweringConfig] = None
    hybrid_search_config: Optional[HybridSearchConfig] = None

class URLDataConfig(BaseModel):
    recursive: bool = True
    return_type: str = 'CHUNKS'
    recursive_url_limit: Optional[int] = None
    ai_enhance_content: Optional[bool] = None
    apify_key: Optional[str] = None
    rescrape_frequency: str = 'Never'

class IndexingConfig(BaseModel):
    index_tables: bool = False
    analyze_documents: bool = False
    enrichment_tasks: Optional[list[str]] = None
    file_processing_implementation: str = 'Default'
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    apify_key: Optional[str] = None

class KnowledgeBase:
    def __init__(
        self,
        id: str,
        name: str,
        file_processing_implementation: str = None,
        chunk_size: int = None,
        chunk_overlap: int = None,
        analyze_documents: bool = False,
    ):
        self.id = id
        self.name = name
        self.file_processing_implementation = file_processing_implementation or 'default'
        self.chunk_size = chunk_size or 400
        self.chunk_overlap = chunk_overlap or 0
        self.analyze_documents = analyze_documents or False

    @classmethod
    def new(
        cls,
        name: str,
        file_processing_implementation: str = None,
        chunk_size: int = None,
        chunk_overlap: int = None,
        analyze_documents: bool = False,
    ) -> 'KnowledgeBase':
        """
        Create a new knowledge base with the specified parameters.
        
        Args:
            name: The name of the knowledge base.
            file_processing_implementation: The implementation to use for processing files. Defaults to 'default'.
            chunk_size: The size of chunks to split documents into. Defaults to 400.
            chunk_overlap: The amount of overlap between chunks. Defaults to 0.
            analyze_documents: Whether to analyze documents for additional metadata. Defaults to False.
            
        Returns:
            A new KnowledgeBase instance.
            
        Raises:
            Exception: If the knowledge base creation fails.
        """
        data = {
            "name": name,
            "file_processing_implementation": file_processing_implementation or 'Default',
            "chunk_size": chunk_size or 400,
            "chunk_overlap": chunk_overlap or 0,
            "analyze_documents": analyze_documents or False,
        }
        response = request_client.request("POST", "/knowledge-base", json=data)
        return cls(response["id"], name)

    @classmethod
    async def anew(
        cls,
        name: str,
        file_processing_implementation: str = None,
        chunk_size: int = None,
        chunk_overlap: int = None,
        analyze_documents: bool = False,
    ) -> 'KnowledgeBase':
        """
        Create a new knowledge base with the specified parameters.
        
        Args:
            name: The name of the knowledge base.
            file_processing_implementation: The implementation to use for processing files. Defaults to 'default'.
            chunk_size: The size of chunks to split documents into. Defaults to 400.
            chunk_overlap: The amount of overlap between chunks. Defaults to 0.
            analyze_documents: Whether to analyze documents for additional metadata. Defaults to False.
            
        Returns:
            A new KnowledgeBase instance.
            
        Raises:
            Exception: If the knowledge base creation fails.
        """
        data = {
            "name": name,
            "file_processing_implementation": file_processing_implementation or 'Default',
            "chunk_size": chunk_size or 400,
            "chunk_overlap": chunk_overlap or 0,
            "analyze_documents": analyze_documents or False,
        }
        response = await async_request_client.arequest("POST", "/knowledge-base", json=data)
        return cls(response["id"], name)

    @classmethod
    def fetch(
        cls,
        id: Optional[str] = None,
        name: Optional[str] = None,
        username: Optional[str] = None,
        org_name: Optional[str] = None,
    ) -> 'KnowledgeBase':
        """
        Fetch an existing knowledge base using its ID or name.
        
        Args:
            id: The ID of the knowledge base to fetch.
            name: The name of the knowledge base to fetch.
            username: Optional username of the knowledge base owner.
            org_name: Optional organization name of the knowledge base owner.
            
        Returns:
            A KnowledgeBase instance representing the fetched knowledge base.
            
        Raises:
            ValueError: If neither id nor name is provided.
            Exception: If the knowledge base fetch fails.
        """
        if id is None and name is None:
            raise ValueError("Either id or name must be provided")
        query = {}
        if id is not None:
            query["id"] = id
        if name is not None:
            query["name"] = name
        if username is not None:
            query["username"] = username
        if org_name is not None:
            query["org_name"] = org_name
        response = request_client.request("GET", f"/knowledge-base", query=query)
        obj = response['object']
        return cls(
            obj['_id'],
            obj['name'],
            obj['fileProcessingImplementation'],
            obj['chunkSize'],
            obj['chunkOverlap'],
            obj['analyzeDocuments'],
        )
    
    def to_dict(self) -> dict:
        return {
            'object_id': self.id,
            'object_type': 'KnowledgeBase',
            'branch_id': None,
            'version': None,
            'state_id': None
        }

    @classmethod
    async def afetch(
        cls,
        id: Optional[str] = None,
        name: Optional[str] = None,
        username: Optional[str] = None,
        org_name: Optional[str] = None,
    ) -> 'KnowledgeBase':
        """
        Fetch an existing knowledge base using its ID or name.
        
        Args:
            id: The ID of the knowledge base to fetch.
            name: The name of the knowledge base to fetch.
            username: Optional username of the knowledge base owner.
            org_name: Optional organization name of the knowledge base owner.
            
        Returns:
            A KnowledgeBase instance representing the fetched knowledge base.
            
        Raises:
            ValueError: If neither id nor name is provided.
            Exception: If the knowledge base fetch fails.
        """
        if id is None and name is None:
            raise ValueError("Either id or name must be provided")
        query = {}
        if id is not None:
            query["id"] = id
        if name is not None:
            query["name"] = name
        if username is not None:
            query["username"] = username
        if org_name is not None:
            query["org_name"] = org_name
        response = await async_request_client.arequest("GET", f"/knowledge-base", query=query)
        obj = response['object']
        return cls(
            obj['_id'],
            obj['name'],
            obj['fileProcessingImplementation'],
            obj['chunkSize'],
            obj['chunkOverlap'],
            obj['analyzeDocuments'],
        )
    
    def query(
        self,
        queries: list[str],
        context: Optional[str] = None,
        search_metadata: Optional[SearchMetadata] = None,
        query_config: Optional[QueryConfig] = None,
    ) -> dict:
        """
        Query the knowledge base to retrieve relevant chunks or documents based on the provided queries.

        Args:
            queries: A list of query strings to search within the knowledge base.
            context: Optional context string to provide additional information for the query.
            search_metadata: Optional SearchMetadata object to refine the search results.
                - filter: stringified qdrant filter to narrow the search scope.
                - opensearch_filter: stringified opensearch filter to narrow the search scope.
                - group_by_key: key to group the search results.
                - top_k: number of top results to return. Defaults to 5.
            query_config: Optional QueryConfig object to configure the query behavior.
                - rerank_documents: A boolean indicating whether to rerank the documents after retrieval.
                - generate_metadata_filters: A boolean to generate metadata filters automatically.
                - transform_query: A boolean to transform the query for better retrieval.
                - answer_multi_query: A boolean to generate multiple similar queries from the original query to search.
                - expand_query: A boolean to expand the query for broader search results.
                - do_advanced_qa: A boolean to perform advanced question answering.
                - format_context_for_llm: A boolean indicating whether to format the results in a format that is easier to process by language models.
                - generate_ai_doc_summaries: A boolean to generate AI-based document summaries.
                - retrieval_unit: A string specifying the unit of retrieval, such as 'document' or 'chunk'.
                - score_cutoff: A float to set a threshold for the minimum score of retrieved documents.
                - retrieval_config: A RetrievalConfig object to configure retrieval specifics.
                    - max_documents: An integer specifying the maximum number of documents to retrieve.
                    - data_fusion_method: A string indicating the method to fuse data vector db and document db.
                - reranking_config: A RerankingConfig object to configure reranking specifics.
                    - reranking_model: A string specifying the model to use for reranking.
                    - api_key: A string for the API key required for reranking services.
                    - num_chunks_to_rerank: An integer specifying the number of chunks to rerank.
                - question_answering_config: A QuestionAnsweringConfig object to configure QA specifics.
                    - qa_model: A string specifying the model to use for question answering.
                    - advanced_qa_mode: A string indicating the mode for advanced question answering (fast/accurate).
                - hybrid_search_config: A HybridSearchConfig object to configure hybrid search specifics.
                    - alpha: A float to set the weight for document db and vector db search results.
                    - fusion_method: A string specifying the method to fuse search results from vector db and document db.

        Returns:
            A dictionary containing the search results, including relevant chunks or documents.

        Raises:
            Exception: If the query execution fails.
        """
        data = {}
        data["queries"] = queries
        if context is not None:
            data["context"] = context
        search_metadata = search_metadata or SearchMetadata()
        query_config = query_config or QueryConfig()
        
        search_metadata = search_metadata.model_dump()
        query_config = query_config.model_dump()

        data["search_metadata"] = search_metadata
        
        data["config"] = query_config
        
        response = request_client.request("POST", f"/knowledge-base/{self.id}/query", json=data)
        return response

    async def aquery(
        self,
        queries: list[str],
        context: Optional[str] = None,
        search_metadata: Optional[SearchMetadata] = None,
        query_config: Optional[QueryConfig] = None,
    ) -> dict:
        """
        Query the knowledge base to retrieve relevant chunks or documents based on the provided queries.

        Args:
            queries: A list of query strings to search within the knowledge base.
            context: Optional context string to provide additional information for the query.
            search_metadata: Optional SearchMetadata object to refine the search results.
                - filter: stringified qdrant filter to narrow the search scope.
                - opensearch_filter: stringified opensearch filter to narrow the search scope.
                - group_by_key: key to group the search results.
                - top_k: number of top results to return. Defaults to 5.
            query_config: Optional QueryConfig object to configure the query behavior.
                - rerank_documents: A boolean indicating whether to rerank the documents after retrieval.
                - generate_metadata_filters: A boolean to generate metadata filters automatically.
                - transform_query: A boolean to transform the query for better retrieval.
                - answer_multi_query: A boolean to generate multiple similar queries from the original query to search.
                - expand_query: A boolean to expand the query for broader search results.
                - do_advanced_qa: A boolean to perform advanced question answering.
                - format_context_for_llm: A boolean indicating whether to format the results in a format that is easier to process by language models.
                - generate_ai_doc_summaries: A boolean to generate AI-based document summaries.
                - retrieval_unit: A string specifying the unit of retrieval, such as 'document' or 'chunk'.
                - score_cutoff: A float to set a threshold for the minimum score of retrieved documents.
                - retrieval_config: A RetrievalConfig object to configure retrieval specifics.
                    - max_documents: An integer specifying the maximum number of documents to retrieve.
                    - data_fusion_method: A string indicating the method to fuse data vector db and document db.
                - reranking_config: A RerankingConfig object to configure reranking specifics.
                    - reranking_model: A string specifying the model to use for reranking.
                    - api_key: A string for the API key required for reranking services.
                    - num_chunks_to_rerank: An integer specifying the number of chunks to rerank.
                - question_answering_config: A QuestionAnsweringConfig object to configure QA specifics.
                    - qa_model: A string specifying the model to use for question answering.
                    - advanced_qa_mode: A string indicating the mode for advanced question answering (fast/accurate).
                - hybrid_search_config: A HybridSearchConfig object to configure hybrid search specifics.
                    - alpha: A float to set the weight for document db and vector db search results.
                    - fusion_method: A string specifying the method to fuse search results from vector db and document db.

        Returns:
            A dictionary containing the search results, including relevant chunks or documents.

        Raises:
            Exception: If the query execution fails.
        """
        data = {}
        data["queries"] = queries
        if context is not None:
            data["context"] = context
        search_metadata = search_metadata or SearchMetadata()
        query_config = query_config or QueryConfig()
        
        search_metadata = search_metadata.model_dump()
        query_config = query_config.model_dump()

        data["search_metadata"] = search_metadata
        
        data["config"] = query_config
        
        response = await async_request_client.arequest("POST", f"/knowledge-base/{self.id}/query", json=data)
        return response
    
    def index_document(
        self, 
        document_type: str, 
        document: str, 
        url_data_config: Optional[URLDataConfig] = None,
        indexing_config: Optional[IndexingConfig] = None,
        custom_metadata: Optional[dict] = None,
    ) -> dict:
        """
        Upsert a document into the knowledge base for future querying.

        This function allows you to add or update documents of various types 
        (e.g., file, URL, Wikipedia, YouTube, Arxiv) in the knowledge base. 
        These documents can later be used as context for queries.

        Args:
            document_type: The type of the document to be indexed. 
                Supported types include 'file', 'url', 'wikipedia', 'youtube', and 'arxiv'.
            document: The document content or identifier, such as a file path or URL.
            url_data_config: Optional configuration for URL data, applicable if the document type is 'url'.
                - recursive: Whether to recursively fetch content from the URL.
                - return_type: The format in which the content should be returned, defaulting to 'CHUNKS'.
                - recursive_url_limit: Limits the number of URLs to be recursively fetched.
                - ai_enhance_content: Whether to use AI to enhance the content fetched from the URL.
                - apify_key: API key for using Apify services for URL processing.
                - rescrape_frequency: How often the URL should be re-scraped, defaulting to 'Never'.
            indexing_config: Optional configuration for indexing, applicable to all document types.
                - index_tables: Whether tables within documents should be indexed.
                - analyze_documents: Whether to analyze documents for additional metadata.
                - enrichment_tasks: Tasks for enriching the document content, such as summarization.
                - file_processing_implementation: The implementation to use for processing files, defaulting to 'Default'.
                - chunk_size: The size of chunks into which documents should be split.
                - chunk_overlap: The amount of overlap between consecutive chunks.
                - apify_key: API key for using Apify services for document processing.
            custom_metadata: Optional dictionary of custom metadata to associate with the document, use with document type 'file'.

        Returns:
            A dictionary containing the status of the indexing operation and the document_ids of the documents that were indexed.

        Raises:
            ValueError: If an invalid document type is provided.
            Exception: If the indexing operation fails.
        """
        data = {}
        files = None
        
        if document_type == 'file':
            with open(document, 'rb') as file:
                files = [('file_data.file', file)]
                
                file_name = os.path.basename(document)
                mime_type = mimetypes.guess_type(document)[0] or 'application/octet-stream'
                
                data["file_data"] = "true"
                data["file_data.metadata.name"] = file_name
                data["file_data.metadata.mime_type"] = mime_type
                
                if custom_metadata is not None:
                    data["file_data.custom_metadata"] = json.dumps(custom_metadata)
                
                indexing_config = indexing_config or IndexingConfig()
                config = indexing_config.model_dump()
                import json
                data["config"] = json.dumps(config)
                
                response = request_client.request("POST", f"/knowledge-base/{self.id}/index", json=data, files=files)
                return response
        elif document_type == 'url':
            url_data_config = url_data_config or URLDataConfig()
            url_data = {}
            url_request = {}
            url_request["url"] = document
            url_request["recursive"] = url_data_config.recursive
            url_request["return_type"] = url_data_config.return_type
            if url_data_config.recursive_url_limit is not None:
                url_request["url_limit"] = url_data_config.recursive_url_limit
            if url_data_config.ai_enhance_content is not None:
                url_request["ai_enhance_content"] = url_data_config.ai_enhance_content
            if url_data_config.apify_key is not None:
                url_request["apify_key"] = url_data_config.apify_key

            url_data["request"] = url_request
            url_data["rescrape_frequency"] = url_data_config.rescrape_frequency
            data["url_data"] = url_data
        
        elif document_type == 'wikipedia' or document_type == 'youtube' or document_type == 'arxiv':
            data[document_type] = document
        else:
            raise ValueError(f"Invalid document type: {document_type}")
        
        indexing_config = indexing_config or IndexingConfig()
        config = indexing_config.model_dump()
        
        data["config"] = config
            
        response = request_client.request("POST", f"/knowledge-base/{self.id}/index", json=data)
        return response

    async def aindex_document(
        self, 
        document_type: str, 
        document: str, 
        url_data_config: Optional[URLDataConfig] = None,
        indexing_config: Optional[IndexingConfig] = None,
        custom_metadata: Optional[dict] = None,
    ) -> dict:
        """
        Upsert a document into the knowledge base for future querying.

        This function allows you to add or update documents of various types 
        (e.g., file, URL, Wikipedia, YouTube, Arxiv) in the knowledge base. 
        These documents can later be used as context for queries.

        Args:
            document_type: The type of the document to be indexed. 
                Supported types include 'file', 'url', 'wikipedia', 'youtube', and 'arxiv'.
            document: The document content or identifier, such as a file path or URL.
            url_data_config: Optional configuration for URL data, applicable if the document type is 'url'.
                - recursive: Whether to recursively fetch content from the URL.
                - return_type: The format in which the content should be returned, defaulting to 'CHUNKS'.
                - recursive_url_limit: Limits the number of URLs to be recursively fetched.
                - ai_enhance_content: Whether to use AI to enhance the content fetched from the URL.
                - apify_key: API key for using Apify services for URL processing.
                - rescrape_frequency: How often the URL should be re-scraped, defaulting to 'Never'.
            indexing_config: Optional configuration for indexing, applicable to all document types.
                - index_tables: Whether tables within documents should be indexed.
                - analyze_documents: Whether to analyze documents for additional metadata.
                - enrichment_tasks: Tasks for enriching the document content, such as summarization.
                - file_processing_implementation: The implementation to use for processing files, defaulting to 'Default'.
                - chunk_size: The size of chunks into which documents should be split.
                - chunk_overlap: The amount of overlap between consecutive chunks.
                - apify_key: API key for using Apify services for document processing.
            custom_metadata: Optional dictionary of custom metadata to associate with the document, use with document type 'file'.

        Returns:
            A dictionary containing the status of the indexing operation and the document_ids of the documents that were indexed.

        Raises:
            ValueError: If an invalid document type is provided.
            Exception: If the indexing operation fails.
        """
        data = {}
        files = None
        
        if document_type == 'file':
            with open(document, 'rb') as file:
                files = [('file_data.file', file)]
                
                file_name = os.path.basename(document)
                mime_type = mimetypes.guess_type(document)[0] or 'application/octet-stream'
                
                data["file_data"] = "true"
                data["file_data.metadata.name"] = file_name
                data["file_data.metadata.mime_type"] = mime_type
                
                if custom_metadata is not None:
                    data["file_data.custom_metadata"] = json.dumps(custom_metadata)
                
                indexing_config = indexing_config or IndexingConfig()
                config = indexing_config.model_dump()
                import json
                data["config"] = json.dumps(config)
                
                response = await async_request_client.arequest("POST", f"/knowledge-base/{self.id}/index", json=data, files=files)
                return response
        elif document_type == 'url':
            url_data_config = url_data_config or URLDataConfig()
            url_data = {}
            url_request = {}
            url_request["url"] = document
            url_request["recursive"] = url_data_config.recursive
            url_request["return_type"] = url_data_config.return_type
            if url_data_config.recursive_url_limit is not None:
                url_request["url_limit"] = url_data_config.recursive_url_limit
            if url_data_config.ai_enhance_content is not None:
                url_request["ai_enhance_content"] = url_data_config.ai_enhance_content
            if url_data_config.apify_key is not None:
                url_request["apify_key"] = url_data_config.apify_key

            url_data["request"] = url_request
            url_data["rescrape_frequency"] = url_data_config.rescrape_frequency
            data["url_data"] = url_data
        
        elif document_type == 'wikipedia' or document_type == 'youtube' or document_type == 'arxiv':
            data[document_type] = document
        else:
            raise ValueError(f"Invalid document type: {document_type}")
        
        indexing_config = indexing_config or IndexingConfig()
        config = indexing_config.model_dump()
        
        data["config"] = config
            
        response = await async_request_client.arequest("POST", f"/knowledge-base/{self.id}/index", json=data)
        return response
    
    def delete(self) -> dict:
        """
        Delete the knowledge base.
        
        This method permanently removes the knowledge base and all its associated documents.
        
        Returns:
            dict: The response containing the deletion status.
            
        Raises:
            Exception: If there is an error deleting the knowledge base.
        """
        response = request_client.request("DELETE", f"/knowledge-base/{self.id}")
        return response

    async def adelete(self) -> dict:
        """
        Delete the knowledge base.
        
        This method permanently removes the knowledge base and all its associated documents.
        
        Returns:
            dict: The response containing the deletion status.
            
        Raises:
            Exception: If there is an error deleting the knowledge base.
        """
        response = await async_request_client.arequest("DELETE", f"/knowledge-base/{self.id}")
        return response

    def delete_documents(self, document_ids: list[str]) -> dict:
        """
        Delete documents from the knowledge base.
        
        This method allows you to remove specific documents from the knowledge base.
        
        Args:
            document_ids: A list of document IDs to be deleted.
        
        Returns:
            dict: The response containing the deletion status.
            
        Raises:
            Exception: If there is an error deleting the documents.
        """
        document_ids = ",".join(document_ids)
        query = {"document_ids": document_ids}
        response = request_client.request(
            "DELETE", f"/knowledge-base/{self.id}/documents", query=query
        )
        return response

    async def adelete_documents(self, document_ids: list[str]) -> dict:
        """
        Delete documents from the knowledge base.
        
        This method allows you to remove specific documents from the knowledge base.
        
        Args:
            document_ids: A list of document IDs to be deleted.
        
        Returns:
            dict: The response containing the deletion status.
            
        Raises:
            Exception: If there is an error deleting the documents.
        """
        document_ids = ",".join(document_ids)
        query = {"document_ids": document_ids}
        response = await async_request_client.arequest(
            "DELETE", f"/knowledge-base/{self.id}/documents", query=query
        )
        return response

    def find_documents(
        self,
        title: Optional[str] = None,
        folder_id: Optional[str] = None,
        integration_id: Optional[str] = None,
    ) -> dict:
        """
        Find documents in the knowledge base based on specific criteria.
        
        This method allows you to search for documents in the knowledge base using 
        optional filters such as title, folder ID, or integration ID.

        Args:
            title: Optional title of the document to search for.
            folder_id: Optional folder ID of the document to search for.
            integration_id: Optional integration ID of the document to search for.
        
        Returns:
            dict: The document ids of the documents that match the search criteria.
            
        Raises:
            ValueError: If no valid criteria are provided.
            Exception: If the search operation fails.
        """
        
        query = {}
        if title is not None:
            query["title"] = title
        if folder_id is not None:
            query["folder_id"] = folder_id
        if integration_id is not None:
            query["integration_id"] = integration_id
        if len(query) == 0:
            raise ValueError(
                "At least one out of title, folder_id, or integration_id must be provided"
            )

        response = request_client.request(
            "GET", f"/knowledge-base/{self.id}/documents", query=query
        )
        return response

    async def afind_documents(
        self,
        title: Optional[str] = None,
        folder_id: Optional[str] = None,
        integration_id: Optional[str] = None,
    ) -> dict:
        """
        Find documents in the knowledge base based on specific criteria.
        
        This method allows you to search for documents in the knowledge base using 
        optional filters such as title, folder ID, or integration ID.

        Args:
            title: Optional title of the document to search for.
            folder_id: Optional folder ID of the document to search for.
            integration_id: Optional integration ID of the document to search for.
        
        Returns:
            dict: The document ids of the documents that match the search criteria.
            
        Raises:
            ValueError: If no valid criteria are provided.
            Exception: If the search operation fails.
        """
        
        query = {}
        if title is not None:
            query["title"] = title
        if folder_id is not None:
            query["folder_id"] = folder_id
        if integration_id is not None:
            query["integration_id"] = integration_id
        if len(query) == 0:
            raise ValueError(
                "At least one out of title, folder_id, or integration_id must be provided"
            )

        response = await async_request_client.arequest(
            "GET", f"/knowledge-base/{self.id}/documents", query=query
        )
        return response
