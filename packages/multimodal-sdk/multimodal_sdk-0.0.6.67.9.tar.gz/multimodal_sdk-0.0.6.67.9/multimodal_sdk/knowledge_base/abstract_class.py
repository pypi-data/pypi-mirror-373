from abc import ABC, abstractmethod
from typing import Union, List, Optional, Dict

class AbstractKnowledgeBaseHandler(ABC):
    
    @abstractmethod
    async def create_collection(
        self,
        kb_resource_id: str,
        collection_name: str,
        ingestion_strategy: List[str],
        distance_method: Optional[str] = None,
        main_lang: Optional[str] = None,
        chunk_strategy: Optional[Dict] = None,
        embedding_strategy: Optional[Dict] = None,
        **kwargs
    ) -> Dict:
        """Create a new collection within a knowledge base and return its details."""
        pass

    @abstractmethod
    async def get_collection(
        self,
        kb_resource_id: str,
        **kwargs
    ) -> Dict:
        """Retrieve the details of a specific collection within a knowledge base."""
        pass

    @abstractmethod
    async def delete_collection(
        self,
        kb_resource_id: str,
        collection_name: str,
        **kwargs
    ) -> Dict:
        """Delete a specific collection within a knowledge base."""
        pass

    @abstractmethod
    async def ingest_data(
        self,
        kb_resource_id: str,
        ingestion_type: Union[str, List[str]],
        texts: Optional[Union[str, List[str]]] = None,
        data: Optional[Union[str, List[str]]] = None,
        ids: Optional[Union[str, List[str]]] = None,
        **kwargs
    ) -> Dict:
        """Ingest data into the specified collection within a knowledge base."""
        pass

    @abstractmethod
    async def retrieve_data(
        self,
        kb_resource_id: str,
        queries: list,
        includes: Optional[list] = [],
        options: Optional[list] = [],
        threshold: Optional[float] = 0.7,
        limit: Optional[int] = 5,
        timeout: Optional[int] = 20,
        **kwargs
    ) -> Dict:
        """Retrieve data from the specified collection within a knowledge base."""
        pass

    # @abstractmethod
    # async def update_collection(self, collection_id: str, kb_resource_id: str, update_details: dict, access_token: str, refresh_token: str) -> dict:
    #     """Update the details of a specific collection within a knowledge base."""
    #     pass

    # @abstractmethod
    # async def ingest_data(self, kb_id: str, ingestion_details: dict, access_token: str, refresh_token: str) -> dict:
    #     """Ingest data into the specified knowledge base."""
    #     pass

    # @abstractmethod
    # async def retrieve_data(self, kb_id: str, access_token: str, refresh_token: str, options: dict = None, includes: list = None, limit: int = 5, queries: dict = None) -> list:
    #     """Retrieve data from the specified knowledge base with optional filtering and query parameters."""
    #     pass
