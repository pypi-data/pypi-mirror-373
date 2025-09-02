import os
from typing import Any, Dict, List, Optional, Tuple
from langchain_community.embeddings.mlflow import MlflowEmbeddings
from langchain_core.documents import Document
from fairo.settings import get_mlflow_gateway_embeddings_route, get_mlflow_gateway_uri, get_fairo_api_key, get_fairo_api_secret, get_fairo_base_url
from fairo.core.client.client import BaseClient
import requests
AWS_AI_EMBEDDING_MODEL = 'cohere.embed-english-v3'


class BaseVectorStore:
    pass

class FairoVectorStore(BaseVectorStore):
    """
    A vector store implementation using the Fairo API
    """

    def __init__(
            self,
            collection_name: str,
            username: str = None,
            password: str = None,
            api_url: str = None,
            embedding_model_id: str = AWS_AI_EMBEDDING_MODEL,
            region_name: str = None,
            collection_metadata: dict = None,
            create_if_not_exists: bool = True
    ):
        """
        Initialize a Fairo vector store client
        
        Args:
            collection_name: Name of the collection
            username: Fairo API username for authentication
            password: Fairo API password for authentication
            api_url: Fairo API base URL
            embedding_model_id: Bedrock embedding model ID
            region_name: AWS region for Bedrock
            collection_metadata: Dict for metadata to add to collection
            create_if_not_exists: Whether to create the collection if it doesn't exist
        """
        self.collection_name = collection_name

        # Get credentials from parameters or environment
        self.username = username or get_fairo_api_key()
        self.password = password or get_fairo_api_secret()
        self.api_url = api_url or get_fairo_base_url()
        self.fairo_auth_token = os.environ.get("FAIRO_AUTH_TOKEN")
        # Setup credentials
        if not self.fairo_auth_token and (not self.username or not self.password):
            raise ValueError("Fairo API credentials must be provided either as FAIRO_AUTH_TOKEN or as parameters or in the FAIRO_USERNAME and FAIRO_PASSWORD environment variables")

        if(self.username and self.password):
            os.environ["MLFLOW_TRACKING_USERNAME"] = self.username
            os.environ["MLFLOW_TRACKING_PASSWORD"] = self.password
            
        # Initialize API client
        self.client = BaseClient(
            base_url=self.api_url.rstrip('/'),
            username=self.username,
            password=self.password,
            fairo_auth_token=self.fairo_auth_token
        )

        # Set up embeddings
        self.embeddings = MlflowEmbeddings(
            target_uri=get_mlflow_gateway_uri(),
            endpoint=get_mlflow_gateway_embeddings_route(),
        )

        self.collection_metadata = collection_metadata or {}
        self.collection_uuid = None

        # Create or retrieve collection
        if create_if_not_exists:
            self._create_or_get_collection()

    def _create_or_get_collection(self) -> None:
        """
        Create a new collection or get an existing one by name
        """
        try:
            # First try to find if collection exists
            collections_data = self.client.get("/collection_stores")

            # Check if our collection exists
            for collection in collections_data.get("results", []):
                if collection.get("name") == self.collection_name:
                    self.collection_uuid = collection.get("uuid")
                    print(f"Found existing collection '{self.collection_name}' with UUID: {self.collection_uuid}")
                    return

            # If collection doesn't exist, create a new one
            if not self.collection_uuid:
                create_data = {
                    "name": self.collection_name,
                    "description": f"Collection for {self.collection_name}",
                    "cmetadata": self.collection_metadata
                }

                collection_data = self.client.post("/collection_stores", json=create_data)
                self.collection_uuid = collection_data.get("uuid")
                print(f"Created new collection '{self.collection_name}' with UUID: {self.collection_uuid}")

        except requests.exceptions.HTTPError as e:
            raise Exception(f"Failed to create or get collection: {str(e)}")

    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to the Fairo vector store
        
        Args:
            documents: List of Document objects to add
        """
        if not documents:
            return

        if not self.collection_uuid:
            self._create_or_get_collection()

        # Convert documents to Fairo format
        docs_data = []
        for doc in documents:
            # Generate embeddings for the document content
            embedding = self.embeddings.embed_query(doc.page_content)

            # Create doc entry (let Fairo API generate document IDs)
            doc_entry = {
                "page_content": doc.page_content,
                "metadata": doc.metadata
            }
            docs_data.append(doc_entry)

        # Send request to Fairo API
        try:
            payload = {"docs": docs_data}
            self.client.post(f"/collection_stores/{self.collection_uuid}/add_documents", json=payload)
            print(f"Successfully added {len(documents)} documents to Fairo collection")

        except requests.exceptions.HTTPError as e:
            raise Exception(f"Failed to add documents: {str(e)}")

    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Add texts with optional metadata to the Fairo vector store
        
        Args:
            texts: List of text strings to add
            metadatas: Optional list of metadata dictionaries
        """
        if not texts:
            return

        # Convert to Document objects
        documents = []
        for i, text in enumerate(texts):
            metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
            documents.append(Document(page_content=text, metadata=metadata))

        # Add to vector store
        self.add_documents(documents)

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        Search for documents similar to the query string
        
        Args:
            query: The search query
            k: Number of results to return
            
        Returns:
            List of Document objects
        """
        # Get search results with scores
        results_with_scores = self.similarity_search_with_score(query, k=k)

        # Extract just the documents
        return [doc for doc, _ in results_with_scores]

    def similarity_search_with_score(self, query: str, k: int = 4) -> List[Tuple[Document, float]]:
        """
        Search for documents similar to the query string and return scores
        
        Args:
            query: The search query
            k: Number of results to return
            
        Returns:
            List of (Document, score) tuples
        """
        if not self.collection_uuid:
            self._create_or_get_collection()

        try:

            payload = {
                "query": query,
            }
            if k:
                payload["k"] = k

            # Send search request
            search_results = self.client.post(
                f"/collection_stores/{self.collection_uuid}/similarity_search", 
                json=payload
            )

            # Process search results
            results = []

            for result in search_results:
                # Create Document object
                doc = Document(
                    page_content=result.get("page_content", ""),
                    metadata=result.get("metadata", {})
                )
                score = result.get("score", 0.0)
                results.append((doc, score))

            return results

        except requests.exceptions.HTTPError as e:
            raise Exception(f"Search failed: {str(e)}")

    def get_by_id(self, document_id: str) -> Optional[Document]:
        """
        Retrieve a document by its ID
        
        Args:
            document_id: The ID of the document to retrieve
            
        Returns:
            Document object if found, None otherwise
        """
        if not self.collection_uuid:
            self._create_or_get_collection()

        try:
            # In a real implementation, we would likely have a specific endpoint for this
            # In the absence of that, we'll use a search query with a filter

            # We need to create a filter condition to search by ID
            # This implementation will depend on how Fairo's API actually handles filters
            payload = {
                "filter": {
                    "metadata": {
                        "id": document_id
                    }
                },
                "k": 1,
                "include_text": True,
                "include_metadata": True
            }

            # Send request
            search_results = self.client.post(
                f"/collection_stores/{self.collection_uuid}/similarity_search",
                json=payload
            )

            # Process response
            results = search_results.get("results", [])

            if not results:
                return None

            # Create Document from the first result
            result = results[0]
            return Document(
                page_content=result.get("text", ""),
                metadata=result.get("metadata", {})
            )

        except requests.exceptions.HTTPError as e:
            print(f"Error retrieving document by ID: {str(e)}")
            return None

    def delete(self) -> None:
        """Delete the collection from Fairo."""
        if not self.collection_uuid:
            return

        try:
            self.client.delete(f"/collection_stores/{self.collection_uuid}")
            print(f"Collection '{self.collection_name}' deleted successfully")
            self.collection_uuid = None

        except requests.exceptions.HTTPError as e:
            print(f"Error deleting collection: {str(e)}")

    @classmethod
    def from_existing(cls, 
                     collection_name: str,
                     username: str = None,
                     password: str = None,
                     api_url: str = get_fairo_base_url(),
                     embedding_model_id: str = AWS_AI_EMBEDDING_MODEL,
                     region_name: str = None):
        """
        Load an existing collection from Fairo.
        
        Args:
            collection_name: Name of the existing collection
            username: Fairo API username
            password: Fairo API password
            api_url: Fairo API base URL
            embedding_model_id: Bedrock embedding model ID
            region_name: AWS region for Bedrock
            
        Returns:
            FairoVectorStore instance connected to the existing collection
        """
        return cls(
            collection_name=collection_name,
            username=username,
            password=password,
            api_url=api_url,
            embedding_model_id=embedding_model_id,
            region_name=region_name,
            create_if_not_exists=False
        )
