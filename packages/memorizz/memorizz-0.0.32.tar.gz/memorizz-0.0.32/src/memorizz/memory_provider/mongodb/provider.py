import time
import logging
from bson import ObjectId
from pymongo import MongoClient
from ..base import MemoryProvider
from dataclasses import dataclass
from ...enums.memory_type import MemoryType
from ...memagent import MemAgentModel
from ...long_term_memory.semantic.persona.persona import Persona
from ...long_term_memory.semantic.persona.role_type import RoleType
from typing import Dict, Any, Optional, List, Union
from pymongo.operations import SearchIndexModel
from ...embeddings import get_embedding, get_embedding_dimensions

logger = logging.getLogger(__name__)

@dataclass
class MongoDBConfig():
    """Configuration for the MongoDB provider."""

    def __init__(self, uri: str, db_name: str = "memorizz", lazy_vector_indexes: bool = False, embedding_provider = None, embedding_config: Dict[str, Any] = None):
        """
        Initialize the MongoDB provider with configuration settings.
        
        Parameters:
        -----------
        uri : str
            The MongoDB URI.
        db_name : str
            The database name.
        lazy_vector_indexes : bool
            If True, vector indexes are created only when needed (when vector operations are performed).
            If False, vector indexes are created immediately during initialization (requires embedding configuration).
            Default: False (maintains backward compatibility)
        embedding_provider : str or EmbeddingManager, optional
            Embedding provider to use. Can be:
            - EmbeddingManager instance (explicit injection)
            - String provider name ("openai", "ollama", "voyageai") 
            - None (uses global embedding configuration)
        embedding_config : Dict[str, Any], optional
            Configuration for the embedding provider. Only used when embedding_provider is a string.
            Example: {"model": "text-embedding-3-small", "dimensions": 512}
        """
        self.uri = uri
        self.db_name = db_name
        self.lazy_vector_indexes = lazy_vector_indexes
        self.embedding_provider = embedding_provider
        self.embedding_config = embedding_config or {}


class MongoDBProvider(MemoryProvider):
    """MongoDB implementation of the MemoryProvider interface."""
    
    def __init__(self, config: MongoDBConfig):
        """
        Initialize the MongoDB provider with configuration settings.
        
        Parameters:
        -----------
        config : MongoDBConfig
            Configuration dictionary containing:
            - 'uri': MongoDB URI
            - 'db_name': Database name
            - 'lazy_vector_indexes': Whether to defer vector index creation
            - 'embedding_provider': Optional explicit embedding provider
        """
        self.config = config
        self.client = MongoClient(config.uri)
        self.db = self.client[config.db_name]
        self.persona_collection = self.db[MemoryType.PERSONAS.value]
        self.toolbox_collection = self.db[MemoryType.TOOLBOX.value]
        self.short_term_memory_collection = self.db[MemoryType.SHORT_TERM_MEMORY.value]
        self.long_term_memory_collection = self.db[MemoryType.LONG_TERM_MEMORY.value]
        self.conversation_memory_collection = self.db[MemoryType.CONVERSATION_MEMORY.value]
        self.workflow_memory_collection = self.db[MemoryType.WORKFLOW_MEMORY.value]
        self.memagent_collection = self.db[MemoryType.MEMAGENT.value]
        self.shared_memory_collection = self.db[MemoryType.SHARED_MEMORY.value]
        self.summaries_collection = self.db[MemoryType.SUMMARIES.value]
        self.semantic_cache_collection = self.db[MemoryType.SEMANTIC_CACHE.value]

        # Track which vector indexes have been created
        self._vector_indexes_created = set()
        
        # Process embedding provider configuration
        self._embedding_provider = self._setup_embedding_provider(config)

        # Create all memory stores in MongoDB.
        self._create_memory_stores()

        # Create vector indexes immediately only if not using lazy initialization
        if not config.lazy_vector_indexes:
            try:
                self._create_vector_indexes_for_memory_stores()
            except Exception as e:
                logger.warning(f"Failed to create vector indexes during initialization: {e}")
                logger.info("Vector indexes will be created lazily when needed")
                # Set lazy mode if immediate creation fails
                self.config.lazy_vector_indexes = True

    def _setup_embedding_provider(self, config: MongoDBConfig):
        """
        Setup the embedding provider based on configuration.
        
        Parameters:
        -----------
        config : MongoDBConfig
            The MongoDB configuration
            
        Returns:
        --------
        EmbeddingManager or None
            The configured embedding provider, or None to use global configuration
        """
        if config.embedding_provider is None:
            # No explicit provider - will use global configuration
            return None
        elif isinstance(config.embedding_provider, str):
            # String provider name - create EmbeddingManager
            try:
                from ...embeddings import EmbeddingManager
                provider = EmbeddingManager(config.embedding_provider, config.embedding_config)
                logger.info(f"Created embedding provider: {provider.get_provider_info()}")
                return provider
            except Exception as e:
                logger.error(f"Failed to create embedding provider '{config.embedding_provider}': {e}")
                raise
        else:
            # Assume it's already an EmbeddingManager instance
            return config.embedding_provider

    def _get_embedding_provider(self):
        """
        Get the embedding provider to use, with fallback logic.
        
        Returns:
        --------
        EmbeddingManager or function
            The embedding provider to use
        """
        if self._embedding_provider is not None:
            # Use explicitly provided embedding provider
            return self._embedding_provider
        else:
            # Fall back to global embedding configuration
            from ...embeddings import get_embedding_manager
            return get_embedding_manager()
    
    def _get_embedding_dimensions_safe(self) -> int:
        """
        Safely get embedding dimensions with error handling.
        
        Returns:
        --------
        int
            The embedding dimensions, or None if not available
        """
        try:
            if self._embedding_provider is not None:
                # Use explicit provider
                return self._embedding_provider.get_dimensions()
            else:
                # Use global configuration
                from ...embeddings import get_embedding_dimensions
                return get_embedding_dimensions()
        except Exception as e:
            logger.error(f"Failed to get embedding dimensions: {e}")
            raise RuntimeError(
                "Cannot determine embedding dimensions. Please configure embeddings first using:\n"
                "configure_embeddings('openai', {'model': 'text-embedding-3-small', 'dimensions': 512})\n"
                "Or use lazy_vector_indexes=True to defer vector index creation."
            )
    
    def _ensure_vector_index_for_collection(self, collection, collection_name: str, memory_store: bool = False):
        """
        Ensure vector index exists for a collection, creating it lazily if needed.
        
        Parameters:
        -----------
        collection : pymongo.Collection
            The MongoDB collection
        collection_name : str  
            Name of the collection (for tracking)
        memory_store : bool
            Whether this is a memory store collection
        """
        index_key = f"{collection_name}_vector_index"
        
        if index_key not in self._vector_indexes_created:
            try:
                self._setup_vector_search_index(collection, "vector_index", memory_store)
                self._vector_indexes_created.add(index_key)
                logger.info(f"Created vector index for collection: {collection_name}")
            except Exception as e:
                logger.error(f"Failed to create vector index for {collection_name}: {e}")
                raise

    def _create_memory_stores(self) -> None:
        """
        Create all memory stores in MongoDB.
        """
        self._create_memory_store(MemoryType.MEMAGENT)
        self._create_memory_store(MemoryType.PERSONAS)
        self._create_memory_store(MemoryType.TOOLBOX)
        self._create_memory_store(MemoryType.SHORT_TERM_MEMORY)
        self._create_memory_store(MemoryType.LONG_TERM_MEMORY)
        self._create_memory_store(MemoryType.CONVERSATION_MEMORY)
        self._create_memory_store(MemoryType.WORKFLOW_MEMORY)
        self._create_memory_store(MemoryType.SHARED_MEMORY)
        self._create_memory_store(MemoryType.SUMMARIES)
    
    def _create_memory_store(self, memory_store_type: MemoryType) -> None:
        """
        Create a new memory store in MongoDB.

        Parameters:
        -----------
        memory_store_type : MemoryType
            The type of memory store to create.

        Returns:
        --------
        None
        """

        # Create collection if it doesn't exist within the database/memory provider
        # Check if the collection exists within the database and if it doesn't, create an empty collection
        for memory_store_type in MemoryType:
            if memory_store_type.value not in self.db.list_collection_names():
                self.db.create_collection(memory_store_type.value)

        

    def _create_vector_indexes_for_memory_stores(self) -> None:
        """
        Create a vector index for each memory store in MongoDB.

        Returns:
        --------
        None
        """
        # Create vector indexes for all memory store types
        for memory_store_type in MemoryType:
            # PERSONAS collection doesn't need memory_id filter since it's not memory-scoped
            memory_store_present = memory_store_type != MemoryType.PERSONAS
            
            # Semantic cache needs special handling due to different field name
            if memory_store_type == MemoryType.SEMANTIC_CACHE:
                self._ensure_semantic_cache_vector_index()
            else:
                self._ensure_vector_index(
                    collection=self.db[memory_store_type.value],
                    index_name="vector_index",
                    memory_store=memory_store_present,
                )
            
    def store(self, data: Dict[str, Any], memory_store_type: MemoryType) -> str:
        """
        Store data in MongoDB using only _id field as primary key.
        
        Parameters:
        -----------
        data : Dict[str, Any]
            The document to be stored.
        memory_store_type : MemoryType
            The type of memory store (e.g., "persona", "toolbox", etc.)
        
        Returns:
        --------
        str
            The ID of the inserted/updated document (MongoDB _id).
        """
        # Get the appropriate collection based on memory type
        collection = None
        if memory_store_type == MemoryType.PERSONAS:
            collection = self.persona_collection
        elif memory_store_type == MemoryType.TOOLBOX:
            collection = self.toolbox_collection
        elif memory_store_type == MemoryType.WORKFLOW_MEMORY:
            collection = self.workflow_memory_collection
        elif memory_store_type == MemoryType.SHORT_TERM_MEMORY:
            collection = self.short_term_memory_collection
        elif memory_store_type == MemoryType.LONG_TERM_MEMORY:
            collection = self.long_term_memory_collection
        elif memory_store_type == MemoryType.CONVERSATION_MEMORY:
            collection = self.conversation_memory_collection
        elif memory_store_type == MemoryType.SHARED_MEMORY:
            collection = self.shared_memory_collection
        elif memory_store_type == MemoryType.SUMMARIES:
            collection = self.summaries_collection
        elif memory_store_type == MemoryType.SEMANTIC_CACHE:
            collection = self.semantic_cache_collection

        if collection is None:
            raise ValueError(f"Invalid memory store type: {memory_store_type}")

        # Clean data by removing custom ID fields - only use MongoDB _id
        # Note: conversation_id is preserved for CONVERSATION_MEMORY as it serves a functional purpose
        data_copy = data.copy()
        
        # Remove custom ID fields since we only want to use _id
        custom_id_fields = [
            "persona_id", "tool_id", "workflow_id", "short_term_memory_id", 
            "agent_id"
        ]
        
        # Don't remove conversation_id for conversation memory
        if memory_store_type != MemoryType.CONVERSATION_MEMORY:
            custom_id_fields.append("conversation_id")
            
        # Don't remove long_term_memory_id for long-term memory as it's needed for knowledge linking
        if memory_store_type != MemoryType.LONG_TERM_MEMORY:
            custom_id_fields.append("long_term_memory_id")
        
        # Don't remove agent_id and memory_id for semantic cache as they're needed for filtering and scoping
        if memory_store_type == MemoryType.SEMANTIC_CACHE:
            # Remove agent_id from the removal list to preserve it (we used this for scoped agents semantic cache)
            custom_id_fields = [field for field in custom_id_fields if field != "agent_id"]
            # Don't add memory_id to removal list for semantic cache
        elif memory_store_type == MemoryType.CONVERSATION_MEMORY:
            # Don't remove memory_id for conversation memory as it's needed for conversation history retrieval
            pass  # Keep memory_id for conversation memory
        else:
            # For all other memory types, remove memory_id as before
            custom_id_fields.append("memory_id")
            
        for field in custom_id_fields:
            data_copy.pop(field, None)
        
        # If document has MongoDB _id, update it
        if "_id" in data_copy:
            result = collection.update_one(
                {"_id": data_copy["_id"]},
                {"$set": data_copy},
                upsert=True
            )
            return str(data_copy["_id"])
        else:
            # For new documents, let MongoDB generate _id automatically
            result = collection.insert_one(data_copy)
            return str(result.inserted_id)

    def retrieve_by_query(self, query: Union[Dict[str, Any], str], memory_store_type: MemoryType, limit: int = 1, include_embedding: bool = False, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Retrieve a document from MongoDB.
        
        Parameters:
        -----------
        query : Union[Dict[str, Any], str]
            The query to use for retrieval. For semantic cache, this is a string (search text).
            For other memory types, this is a MongoDB query dict.
        limit : int
            The maximum number of documents to return.
        include_embedding : bool
            Whether to include the embedding field in the results. Default is False for performance.
        
        Returns:
        --------
        Optional[Dict[str, Any]]
            The retrieved document, or None if not found.
        """


        
        # Define projection to exclude embeddings by default
        projection = {} if include_embedding else {"embedding": 0}
        
        if memory_store_type == MemoryType.PERSONAS:
            return self.retrieve_persona_by_query(query, limit=limit)
        elif memory_store_type == MemoryType.TOOLBOX:
            return self.retrieve_toolbox_item(query, limit)
        elif memory_store_type == MemoryType.WORKFLOW_MEMORY:
            return self.retrieve_workflow_by_query(query, limit)
        elif memory_store_type == MemoryType.SHORT_TERM_MEMORY:
            return self.short_term_memory_collection.find(query, projection).limit(limit)
        elif memory_store_type == MemoryType.LONG_TERM_MEMORY:
            return self.long_term_memory_collection.find(query, projection).limit(limit)
        elif memory_store_type == MemoryType.CONVERSATION_MEMORY:
            return self.conversation_memory_collection.find(query, projection).limit(limit)
        elif memory_store_type == MemoryType.SUMMARIES:
            return self.retrieve_summaries_by_query(query, limit)
        elif memory_store_type == MemoryType.SEMANTIC_CACHE:
            # For semantic cache, we need to handle two different cases:
            # 1. Dict query: Loading existing cache entries (e.g., {"agent_id": "xyz"})
            # 2. String query: Semantic similarity search (e.g., "What is Python?")
            if isinstance(query, dict):
                # This is a filter query for loading existing cache entries
                return self.semantic_cache_collection.find(query, {"embedding": 0}).limit(limit)
            else:
                # This is a text query for semantic similarity search
                return self.find_similar_cache_entries(query, limit=limit, **kwargs)
       
    def retrieve_by_id(self, id: str, memory_store_type: MemoryType) -> Optional[Dict[str, Any]]:
        """
        Retrieve a document from MongoDB by _id.

        Parameters:
        -----------
        id : str
            The MongoDB _id of the document to retrieve.
        memory_store_type : MemoryType
            The type of memory store (e.g., "persona", "toolbox", etc.)

        Returns:
        --------
        Optional[Dict[str, Any]]
            The retrieved document, or None if not found.
        """
        # Get the appropriate collection
        collection_mapping = {
            MemoryType.PERSONAS: self.persona_collection,
            MemoryType.TOOLBOX: self.toolbox_collection,
            MemoryType.WORKFLOW_MEMORY: self.workflow_memory_collection,
            MemoryType.SHORT_TERM_MEMORY: self.short_term_memory_collection,
            MemoryType.LONG_TERM_MEMORY: self.long_term_memory_collection,
            MemoryType.CONVERSATION_MEMORY: self.conversation_memory_collection,
            MemoryType.SHARED_MEMORY: self.shared_memory_collection,
            MemoryType.SUMMARIES: self.summaries_collection,
            MemoryType.SEMANTIC_CACHE: self.semantic_cache_collection
        }
        
        collection = collection_mapping.get(memory_store_type)
        if collection is None:
            return None
            
        # Set projection to exclude embedding for performance
        projection = {"embedding": 0} if memory_store_type in [
            MemoryType.PERSONAS, MemoryType.TOOLBOX, MemoryType.WORKFLOW_MEMORY, MemoryType.SUMMARIES
        ] else None
        
        # For semantic cache, exclude embedding by default for performance
        if memory_store_type == MemoryType.SEMANTIC_CACHE:
            projection = {"embedding": 0}
        
        # Retrieve using MongoDB _id only
        try:
            if ObjectId.is_valid(id):
                return collection.find_one({"_id": ObjectId(id)}, projection)
        except Exception:
            pass
            
        return None
    
    def retrieve_by_name(self, name: str, memory_store_type: MemoryType, include_embedding: bool = False) -> Optional[Dict[str, Any]]:
        """
        Retrieve a document from MongoDB by name.
        
        Parameters:
        -----------
        name : str
            The name of the document to retrieve.
        memory_store_type : MemoryType
            The type of memory store to retrieve from.
        include_embedding : bool
            Whether to include the embedding field in the results. Default is False for performance.
        
        Returns:
        --------
        Optional[Dict[str, Any]]
            The retrieved document, or None if not found.
        """
        # Define projection to exclude embeddings by default
        projection = {} if include_embedding else {"embedding": 0}
        
        if memory_store_type == MemoryType.TOOLBOX:
            return self.toolbox_collection.find_one({"name": name}, projection)
        elif memory_store_type == MemoryType.PERSONAS:
            return self.persona_collection.find_one({"name": name}, projection)
        elif memory_store_type == MemoryType.WORKFLOW_MEMORY:
            return self.workflow_memory_collection.find_one({"name": name}, projection)
        elif memory_store_type == MemoryType.SHORT_TERM_MEMORY:
            return self.short_term_memory_collection.find_one({"name": name}, projection)
        elif memory_store_type == MemoryType.LONG_TERM_MEMORY:
            return self.long_term_memory_collection.find_one({"name": name}, projection)
        elif memory_store_type == MemoryType.CONVERSATION_MEMORY:
            return self.conversation_memory_collection.find_one({"name": name}, projection)
        elif memory_store_type == MemoryType.SUMMARIES:
            return self.summaries_collection.find_one({"name": name}, projection)
        


    def retrieve_persona_by_query(self, query: Dict[str, Any], limit: int = 1) -> Optional[Dict[str, Any]]:
        """
        Retrieve a persona or several personas from MongoDB.
        This function uses a vector search to retrieve the most similar personas.

        Parameters:
        -----------
        query : Dict[str, Any]

        Returns:
        --------
        Optional[List[Dict[str, Any]]]
            The retrieved personas, or None if not found.
        """

        # Get the embedding for the query
        try:
            embedding = get_embedding(query)
        except Exception as e:
            logger.error(f"Failed to generate embedding for query: {e}")
            return []

        # Create the vector search pipeline
        pipeline = [
            {
                "$vectorSearch": {
                    "queryVector": embedding,
                    "path": "embedding",
                    "numCandidates": 100,
                    "limit": limit,
                    "index": "vector_index"
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "embedding": 0,
                    "score": { "$meta": "vectorSearchScore" }
                }
            }
        ]

        # Execute the vector search
        results = list(self.persona_collection.aggregate(pipeline))

        # Return the results
        return results if results else None
        

    def retrieve_toolbox_item(self, query: Dict[str, Any], limit: int = 1) -> Optional[Dict[str, Any]]:
        """
        Retrieve a toolbox item or several items from MongoDB.
        This function uses a vector search to retrieve the most similar toolbox items.
        Parameters:
        -----------
        query : Dict[str, Any]
            The query to use for retrieval.
        limit : int
            The maximum number of toolbox items to return.
        
        Returns:
        --------
        Optional[List[Dict[str, Any]]]
            The retrieved toolbox items, or None if not found.
        """

        # Get the embedding for the query
        try:
            embedding = get_embedding(query)
        except Exception as e:
            logger.error(f"Failed to generate embedding for query: {e}")
            return []

        # Create the vector search pipeline
        pipeline = [
            {
                "$vectorSearch": {
                    "queryVector": embedding,
                    "path": "embedding",
                    "numCandidates": 100,
                    "limit": limit,
                    "index": "vector_index"
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "embedding": 0,
                    "score": { "$meta": "vectorSearchScore" }
                }
            }
        ]

        # Execute the vector search
        results = list(self.toolbox_collection.aggregate(pipeline))

        # Return the results
        return results if results else None
    
    def retrieve_workflow_by_query(self, query: Dict[str, Any], limit: int = 1) -> Optional[Dict[str, Any]]:
        """
        Retrieve a workflow or several workflows from MongoDB.
        This function uses a vector search to retrieve the most similar workflows.

        Parameters:
        -----------
        query : Dict[str, Any]
            The query to use for retrieval.
        limit : int
            The maximum number of workflows to return.
            
        Returns:
        --------
        Optional[List[Dict[str, Any]]]
            The retrieved workflows, or None if not found.
        """

        # Get the embedding for the query
        try:
            embedding = get_embedding(query)
        except Exception as e:
            logger.error(f"Failed to generate embedding for query: {e}")
            return []

        # Create the vector search pipeline
        pipeline = [
            {
                "$vectorSearch": {
                    "queryVector": embedding,
                    "path": "embedding",
                    "numCandidates": 100,
                    "limit": limit,
                    "index": "vector_index"
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "embedding": 0,
                    "score": { "$meta": "vectorSearchScore" }
                }
            }
        ]

        # Execute the vector search
        results = list(self.workflow_memory_collection.aggregate(pipeline))

        # Return the results
        return results if results else None

    def retrieve_summaries_by_query(self, query: Dict[str, Any], limit: int = 1) -> Optional[Dict[str, Any]]:
        """
        Retrieve summaries by query using vector search.
        
        Parameters:
        -----------
        query : Dict[str, Any]
            The query to use for retrieval.
        limit : int
            The maximum number of summaries to return.
            
        Returns:
        --------
        Optional[List[Dict[str, Any]]]
            The retrieved summaries, or None if not found.
        """
        # Get the embedding for the query
        try:
            embedding = get_embedding(query)
        except Exception as e:
            logger.error(f"Failed to generate embedding for query: {e}")
            return []

        # Create the vector search pipeline
        pipeline = [
            {
                "$vectorSearch": {
                    "queryVector": embedding,
                    "path": "embedding",
                    "numCandidates": 100,
                    "limit": limit,
                    "index": "vector_index"
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "embedding": 0,
                    "score": { "$meta": "vectorSearchScore" }
                }
            }
        ]

        # Execute the vector search
        results = list(self.summaries_collection.aggregate(pipeline))

        # Return the results
        return results if results else None

    def get_summaries_by_memory_id(self, memory_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve summaries for a specific memory_id, ordered by timestamp (most recent first).
        
        Parameters:
        -----------
        memory_id : str
            The memory_id to retrieve summaries for.
        limit : int
            The maximum number of summaries to return.
            
        Returns:
        --------
        List[Dict[str, Any]]
            List of summaries for the memory_id.
        """
        return list(self.summaries_collection.find(
            {"memory_id": memory_id}, 
            {"embedding": 0}
        ).sort("period_end", -1).limit(limit))

    def get_summaries_by_time_range(self, memory_id: str, start_time: float, end_time: float) -> List[Dict[str, Any]]:
        """
        Retrieve summaries for a specific memory_id within a time range based on the period they cover.
        
        NOTE: This filters by the time period that the summary covers (period_start/period_end),
        not when the summary was created. Use get_summaries_by_creation_time() to filter by creation time.
        
        Parameters:
        -----------
        memory_id : str
            The memory_id to retrieve summaries for.
        start_time : float
            Start timestamp for the memory period range.
        end_time : float
            End timestamp for the memory period range.
            
        Returns:
        --------
        List[Dict[str, Any]]
            List of summaries whose covered period falls within the time range.
        """
        from datetime import datetime
        
        # Convert to ISO string for compatibility with existing string timestamps
        start_iso = datetime.fromtimestamp(start_time).isoformat()
        end_iso = datetime.fromtimestamp(end_time).isoformat()
        
        # Query supports both float and string timestamps
        return list(self.summaries_collection.find({
            "memory_id": memory_id,
            "$or": [
                # Float timestamps (new format)
                {
                    "period_start": {"$gte": start_time, "$type": "number"},
                    "period_end": {"$lte": end_time, "$type": "number"}
                },
                # String timestamps (legacy format)
                {
                    "period_start": {"$gte": start_iso, "$type": "string"},
                    "period_end": {"$lte": end_iso, "$type": "string"}
                }
            ]
        }, {"embedding": 0}).sort("period_start", 1))

    def get_summaries_by_creation_time(self, memory_id: str, start_time: float, end_time: float) -> List[Dict[str, Any]]:
        """
        Retrieve summaries for a specific memory_id created within a time range.
        
        This filters by when the summary was actually created (created_at timestamp),
        not the time period that the summary covers.
        
        Parameters:
        -----------
        memory_id : str
            The memory_id to retrieve summaries for.
        start_time : float
            Start timestamp for when summaries were created.
        end_time : float
            End timestamp for when summaries were created.
            
        Returns:
        --------
        List[Dict[str, Any]]
            List of summaries created within the time range.
        """
        return list(self.summaries_collection.find({
            "memory_id": memory_id,
            "created_at": {"$gte": start_time, "$lte": end_time}
        }, {"embedding": 0}).sort("created_at", -1))

    # ===== SEMANTIC CACHE METHODS =====
    
    def store_semantic_cache_entry(self, cache_entry: Dict[str, Any]) -> str:
        """
        Store a semantic cache entry in the semantic_cache collection.
        
        Parameters:
        -----------
        cache_entry : Dict[str, Any]
            The cache entry containing query, response, embedding, and metadata.
            
        Returns:
        --------
        str
            The ID of the stored cache entry.
        """
        return self.store(cache_entry, MemoryType.SEMANTIC_CACHE)
    
    def find_similar_cache_entries(self, query: str, 
                                  limit: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """
        Find semantically similar cache entries using vector search.
        
        Parameters:
        -----------
        query : str
            The query to search for
        limit : int
            Maximum number of results
        kwargs : Dict[str, Any]
            Additional filters to apply to the query
            
        Returns:
        --------
        List[Dict[str, Any]]
            List of similar cache entries with similarity scores
        """
        
        try:
            embedding = get_embedding(query)
        except Exception as e:
            logger.error(f"Failed to generate embedding for semantic cache query: {e}")
            return []
        

        # Extract the filter from kwargs (agent_id, memory_id, session_id)
        # Build filter conditionally - only include agent_id if present (for LOCAL scope)
        search_filter = {}
        if 'agent_id' in kwargs and kwargs['agent_id'] is not None:
            search_filter['agent_id'] = str(kwargs['agent_id'])
        if 'memory_id' in kwargs and kwargs['memory_id'] is not None:
            search_filter['memory_id'] = str(kwargs['memory_id'])
        if 'session_id' in kwargs and kwargs['session_id'] is not None:
            search_filter['session_id'] = str(kwargs['session_id'])

        # Get the embedding for the query
        # Construct the vector search stage
        vector_search_stage = {
            "$vectorSearch": {
                "queryVector": embedding,
                "path": "embedding",
                "numCandidates": 100,
                "limit": limit,
                "index": "vector_index"
            }
        }
        
        # Only add filter if we have any filter criteria (enables true GLOBAL scope)
        if search_filter:
            vector_search_stage["$vectorSearch"]["filter"] = search_filter

        # Add projection stage
        project_stage = {
            "$project": {
                "_id": 0,
                "embedding": 0,
                "score": {"$meta": "vectorSearchScore"},
            }
        }

        pipeline = [vector_search_stage, project_stage]
        
        try:
            result = self.semantic_cache_collection.aggregate(pipeline)
            results = list(result)
            return results
        except Exception as e:
            logger.warning(f"Vector search failed for semantic cache: {e}")
            return []
    
    def update_cache_entry_usage(self, cache_id: str, usage_count: int, last_accessed: float) -> bool:
        """
        Update usage statistics for a cache entry.
        
        Parameters:
        -----------
        cache_id : str
            The MongoDB _id of the cache entry
        usage_count : int
            New usage count
        last_accessed : float
            New last accessed timestamp
            
        Returns:
        --------
        bool
            True if update was successful
        """
        try:
            result = self.semantic_cache_collection.update_one(
                {"_id": ObjectId(cache_id)},
                {
                    "$set": {
                        "usage_count": usage_count,
                        "last_accessed": last_accessed
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.warning(f"Failed to update cache entry usage: {e}")
            return False
    
    def clear_semantic_cache(self, agent_id: Optional[str] = None, 
                           memory_id: Optional[str] = None) -> int:
        """
        Clear semantic cache entries with optional filtering.
        
        Parameters:
        -----------
        agent_id : Optional[str]
            Clear only entries for this agent ID
        memory_id : Optional[str] 
            Clear only entries for this memory ID
            
        Returns:
        --------
        int
            Number of entries deleted
        """
        query = {}
        if agent_id:
            query['agent_id'] = agent_id
        if memory_id:
            query['memory_id'] = memory_id
            
        try:
            result = self.semantic_cache_collection.delete_many(query)
            return result.deleted_count
        except Exception as e:
            logger.warning(f"Failed to clear semantic cache: {e}")
            return 0

    def delete_by_id(self, id: str, memory_store_type: MemoryType) -> bool:
        """
        Delete a document from MongoDB by _id.
        
        Parameters:
        -----------
        id : str
            The MongoDB _id of the document to delete.
        memory_store_type : MemoryType
            The type of memory store (e.g., "persona", "toolbox", etc.)
        
        Returns:
        --------
        bool
            True if deletion was successful, False otherwise.
        """
        # Get the appropriate collection
        collection_mapping = {
            MemoryType.PERSONAS: self.persona_collection,
            MemoryType.TOOLBOX: self.toolbox_collection,
            MemoryType.WORKFLOW_MEMORY: self.workflow_memory_collection,
            MemoryType.SHORT_TERM_MEMORY: self.short_term_memory_collection,
            MemoryType.LONG_TERM_MEMORY: self.long_term_memory_collection,
            MemoryType.CONVERSATION_MEMORY: self.conversation_memory_collection,
            MemoryType.SHARED_MEMORY: self.shared_memory_collection,
            MemoryType.SUMMARIES: self.summaries_collection,
            MemoryType.SEMANTIC_CACHE: self.semantic_cache_collection
        }
        
        collection = collection_mapping.get(memory_store_type)
        if collection is None:
            return False
            
        # Delete using MongoDB _id only
        try:
            if ObjectId.is_valid(id):
                result = collection.delete_one({"_id": ObjectId(id)})
                return result.deleted_count > 0
        except Exception:
            pass
            
        return False
    
    def delete_by_name(self, name: str, memory_store_type: MemoryType) -> bool:
        """
        Delete a document from MongoDB by name.

        Parameters:
        -----------
        name : str
            The name of the document to delete.
        memory_store_type : MemoryType
            The type of memory store (e.g., "persona", "toolbox", etc.)
        
        Returns:
        --------
        bool
            True if deletion was successful, False otherwise.
        """
        if memory_store_type == MemoryType.TOOLBOX:
            result = self.toolbox_collection.delete_one({"name": name})
        elif memory_store_type == MemoryType.PERSONAS:
            result = self.persona_collection.delete_one({"name": name})
        elif memory_store_type == MemoryType.SHORT_TERM_MEMORY:
            result = self.short_term_memory_collection.delete_one({"name": name})
        elif memory_store_type == MemoryType.LONG_TERM_MEMORY:
            result = self.long_term_memory_collection.delete_one({"name": name}) 
        elif memory_store_type == MemoryType.CONVERSATION_MEMORY:
            result = self.conversation_memory_collection.delete_one({"name": name})
        elif memory_store_type == MemoryType.WORKFLOW_MEMORY:
            result = self.workflow_memory_collection.delete_one({"name": name})
        elif memory_store_type == MemoryType.SUMMARIES:
            result = self.summaries_collection.delete_one({"name": name})
        else:
            return False
        
        return result.deleted_count > 0

    def delete_all(self, memory_store_type: MemoryType) -> bool:
        """
        Delete all documents within a memory store type in MongoDB.
        
        Parameters:
        -----------
        memory_store_type : MemoryType
            The type of memory store (e.g., "persona", "toolbox", etc.)
        
        Returns:
        --------
        bool
            True if deletion was successful, False otherwise.
        """
        if memory_store_type == MemoryType.PERSONAS:
            result = self.persona_collection.delete_many({})
        elif memory_store_type == MemoryType.TOOLBOX:
            result = self.toolbox_collection.delete_many({})
        elif memory_store_type == MemoryType.SHORT_TERM_MEMORY:
            result = self.short_term_memory_collection.delete_many({})
        elif memory_store_type == MemoryType.LONG_TERM_MEMORY:
            result = self.long_term_memory_collection.delete_many({})
        elif memory_store_type == MemoryType.CONVERSATION_MEMORY:
            result = self.conversation_memory_collection.delete_many({})
        elif memory_store_type == MemoryType.WORKFLOW_MEMORY:
            result = self.workflow_memory_collection.delete_many({})
        elif memory_store_type == MemoryType.SUMMARIES:
            result = self.summaries_collection.delete_many({})
        else:
            return False
            
        return result.deleted_count > 0
            
    
    def list_all(self, memory_store_type: MemoryType, include_embedding: bool = False) -> List[Dict[str, Any]]:
        """
        List all documents within a memory store type in MongoDB.

        Parameters:
        -----------
        memory_store_type : MemoryType
            The type of memory store (e.g., "persona", "toolbox", etc.)
        include_embedding : bool
            Whether to include the embedding field in the results. Default is False for performance.
        
        Returns:
        --------
        List[Dict[str, Any]]
            The list of all documents from MongoDB.
        """
        # Define projection to exclude embeddings by default
        projection = {} if include_embedding else {"embedding": 0}

        if memory_store_type == MemoryType.PERSONAS:
            return list(self.persona_collection.find({}, projection))
        elif memory_store_type == MemoryType.TOOLBOX:
            return list(self.toolbox_collection.find({}, projection))
        elif memory_store_type == MemoryType.SHORT_TERM_MEMORY:
            return list(self.short_term_memory_collection.find({}, projection))
        elif memory_store_type == MemoryType.LONG_TERM_MEMORY:
            return list(self.long_term_memory_collection.find({}, projection))
        elif memory_store_type == MemoryType.CONVERSATION_MEMORY:
            return list(self.conversation_memory_collection.find({}, projection))
        elif memory_store_type == MemoryType.WORKFLOW_MEMORY:
            return list(self.workflow_memory_collection.find({}, projection))
        elif memory_store_type == MemoryType.SHARED_MEMORY:
            return list(self.shared_memory_collection.find({}, projection))
        elif memory_store_type == MemoryType.SUMMARIES:
            return list(self.summaries_collection.find({}, projection))
        else:
            logger.warning(f"Unsupported memory store type for list_all: {memory_store_type}")
            return []
        
    def update_by_id(self, id: str, data: Dict[str, Any], memory_store_type: MemoryType) -> bool:
        """
        Update a document in a memory store type in MongoDB by _id.

        Parameters:
        -----------
        id : str
            The MongoDB _id of the document to update.
        data : Dict[str, Any]
            The data to update the document with.
        memory_store_type : MemoryType
            The type of memory store (e.g., "persona", "toolbox", etc.)
        
        Returns:
        --------
        bool
            True if update was successful, False otherwise.
        """
        # Get the appropriate collection
        collection_mapping = {
            MemoryType.PERSONAS: self.persona_collection,
            MemoryType.TOOLBOX: self.toolbox_collection,
            MemoryType.WORKFLOW_MEMORY: self.workflow_memory_collection,
            MemoryType.SHORT_TERM_MEMORY: self.short_term_memory_collection,
            MemoryType.LONG_TERM_MEMORY: self.long_term_memory_collection,
            MemoryType.CONVERSATION_MEMORY: self.conversation_memory_collection,
            MemoryType.SHARED_MEMORY: self.shared_memory_collection,
            MemoryType.SUMMARIES: self.summaries_collection,
            MemoryType.SEMANTIC_CACHE: self.semantic_cache_collection
        }
        
        collection = collection_mapping.get(memory_store_type)
        if collection is None:
            logger.error(f"No collection mapping found for memory store type: {memory_store_type}")
            return False
            
        # Update using MongoDB _id only
        try:
            if ObjectId.is_valid(id):
                result = collection.update_one({"_id": ObjectId(id)}, {"$set": data})
                success = result.modified_count > 0
                if not success:
                    logger.warning(f"Update operation found no documents to modify for id: {id}")
                return success
            else:
                logger.error(f"Invalid ObjectId: {id}")
                return False
        except Exception as e:
            logger.error(f"Error updating document with id {id}: {e}", exc_info=True)
            return False
            
            
    def update_toolbox_item(self, id: str, data: Dict[str, Any]) -> bool:
        """
        Update a toolbox item in MongoDB by id using optimized queries.
        """

        # Update the embedding if the name, docstring or signature has changed

        # Get the old data
        old_data = self.retrieve_by_id(id, MemoryType.TOOLBOX)
        if not old_data:
            return False

        # Concatenate the name, docstring and signature if any of them have changed
        if old_data.get("name") != data.get("name"):
            data["name"] = data.get("name", old_data.get("name", ""))
        if old_data.get("docstring") != data.get("docstring"):
            data["docstring"] = data.get("docstring", old_data.get("docstring", ""))
        if old_data.get("signature") != data.get("signature"):
            data["signature"] = data.get("signature", old_data.get("signature", ""))

        # Update the embedding
        data["embedding"] = get_embedding(data["name"] + " " + data["docstring"] + " " + data["signature"])

        # Use the optimized update_by_id method
        return self.update_by_id(id, data, MemoryType.TOOLBOX)
    

    def retrieve_conversation_history_ordered_by_timestamp(self, memory_id: str, include_embedding: bool = False) -> List[Dict[str, Any]]:
        """
        Retrieve the conversation history ordered by timestamp.

        Parameters:
        -----------
        memory_id : str
            The id of the memory to retrieve the conversation history for.
        include_embedding : bool
            Whether to include the embedding field in the results. Default is False for performance.

        Returns:
        --------
        List[Dict[str, Any]]
            The conversation history ordered by timestamp.
        """
        projection = {} if include_embedding else {"embedding": 0}
        results = list(self.conversation_memory_collection.find({"memory_id": memory_id}, projection).sort("timestamp", 1))
        logger.debug(f"Retrieved {len(results)} conversation items for memory_id: {memory_id}")
        return results
    
    def retrieve_memory_units_by_query(self, query: str = None, query_embedding: list[float] = None, memory_id: str = None, memory_type: MemoryType = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve memory units by query.

        Parameters:
        -----------
        query : str
            The query to use for retrieval.
        query_embedding : list[float]
            The embedding of the query.
        memory_id : str
            The id of the memory to retrieve the memory units for.
        memory_type : MemoryType
            The type of memory to retrieve the memory units for.
        limit : int
            The maximum number of memory units to return.

        Returns:
        --------
        List[Dict[str, Any]]
            The memory units ordered by timestamp.
        """

        # Detect the memory type
        if memory_type == MemoryType.CONVERSATION_MEMORY:
            return self.get_conversation_memory_units(query, query_embedding, memory_id, limit)
        elif memory_type == MemoryType.WORKFLOW_MEMORY:
            return self.get_workflow_memory_units(query, query_embedding, memory_id, limit)
        elif memory_type == MemoryType.SUMMARIES:
            return self.get_summaries_memory_units(query, query_embedding, memory_id, limit)
        else:
            # Return empty list for unsupported memory types
            return []


    def get_conversation_memory_units(self, query: str = None, query_embedding: list[float] = None, memory_id: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the conversation memory units.

        Parameters:
        -----------
        query : str
            The query to use for retrieval.
        query_embedding : list[float]
            The embedding of the query.
        memory_id : str
            The id of the memory to retrieve the memory units for.
        limit : int
            The maximum number of memory units to return.

        Returns:
        --------
        List[Dict[str, Any]]
            The memory units ordered by timestamp.
        """

        # Ensure vector index exists for conversation memory (lazy creation)
        if self.config.lazy_vector_indexes:
            self._ensure_vector_index_for_collection(
                self.conversation_memory_collection, 
                "conversation_memory", 
                memory_store=True
            )

        # If the query embedding is not provided, then we create it
        if query_embedding is None and query is not None:
            try:
                query_embedding = get_embedding(query)
            except Exception as e:
                logger.error(f"Failed to generate embedding for query: {e}")
                return []

        vector_stage = {
            "$vectorSearch": {
                "index": "vector_index",
                "queryVector": query_embedding,
                "path": "embedding",
                "numCandidates": 100,
                "limit": limit,
                "filter": {"memory_id": memory_id}
            }
        }

        # Add the vector stage to the pipeline
        pipeline = [
            vector_stage,
            {"$addFields": {"score": {"$meta": "vectorSearchScore"}}},
            {"$project": {"embedding": 0}},
            {"$sort": {"score": -1, "timestamp": 1}},
        ]

        # Execute the pipeline
        results = list(self.conversation_memory_collection.aggregate(pipeline))

        # Return the results
        return results

    def get_summaries_memory_units(self, query: str = None, query_embedding: list[float] = None, memory_id: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the summaries memory units.

        Parameters:
        -----------
        query : str
            The query to use for retrieval.
        query_embedding : list[float]
            The embedding of the query.
        memory_id : str
            The id of the memory to retrieve the memory units for.
        limit : int
            The maximum number of memory units to return.

        Returns:
        --------
        List[Dict[str, Any]]
            The memory units ordered by timestamp.
        """

        # If the query embedding is not provided, then we create it
        if query_embedding is None and query is not None:
            try:
                query_embedding = get_embedding(query)
            except Exception as e:
                logger.error(f"Failed to generate embedding for query: {e}")
                return []

        vector_stage = {
            "$vectorSearch": {
                "index": "vector_index",
                "queryVector": query_embedding,
                "path": "embedding",
                "numCandidates": 100,
                "limit": limit,
                "filter": {"memory_id": memory_id}
            }
        }

        # Add the vector stage to the pipeline
        pipeline = [
            vector_stage,
            {"$addFields": {"score": {"$meta": "vectorSearchScore"}}},
            {"$project": {"embedding": 0}},
            {"$sort": {"score": -1, "created_at": -1}},
        ]

        # Execute the pipeline
        results = list(self.summaries_collection.aggregate(pipeline))

        # Return the results
        return results

    def get_workflow_memory_units(self, query: str = None, query_embedding: list[float] = None, memory_id: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the workflow memory units.

        Parameters:
        -----------
        query : str
            The query to use for retrieval.
        query_embedding : list[float]
            The embedding of the query.
        memory_id : str
            The id of the memory to retrieve the memory units for.
        limit : int
            The maximum number of memory units to return.

        Returns:
        --------
        List[Dict[str, Any]]
            The memory units ordered by timestamp.
        """

        # Ensure vector index exists for workflow memory (lazy creation)
        if self.config.lazy_vector_indexes:
            self._ensure_vector_index_for_collection(
                self.workflow_memory_collection,
                "workflow_memory", 
                memory_store=True
            )

        # If the query embedding is not provided, then we create it
        if query_embedding is None and query is not None:
            try:
                query_embedding = get_embedding(query)
            except Exception as e:
                logger.error(f"Failed to generate embedding for query: {e}")
                return []

        vector_stage = {
            "$vectorSearch": {
                "index": "vector_index",
                "queryVector": query_embedding,
                "path": "embedding",
                "numCandidates": 100,
                "limit": limit,
                "filter": {"memory_id": memory_id}
            }
        }

        # Add the vector stage to the pipeline
        pipeline = [
            vector_stage,
            {"$addFields": {"score": {"$meta": "vectorSearchScore"}}},
            {"$project": {"embedding": 0}},
            {"$sort": {"score": -1, "timestamp": 1}},
        ]

        # Execute the pipeline
        results = list(self.workflow_memory_collection.aggregate(pipeline))

        # Return the results
        return results
    
    def store_memagent(self, memagent: "MemAgentModel") -> "MemAgentModel":
        """
        Store a memagent in the MongoDB database using only _id field.
        
        Parameters:
        -----------
        memagent : MemAgentModel
            The memagent to be stored.
        
        Returns:
        --------
        MemAgentModel
            The stored memagent.
        """
        # Convert the MemAgentModel to a dictionary
        memagent_dict = memagent.model_dump()
        
        # Remove agent_id field since we only want to use _id
        memagent_dict.pop("agent_id", None)
        
        # Convert persona to a serializable format if it exists
        if memagent.persona:
            # Store the entire persona object as a serializable dictionary
            memagent_dict["persona"] = memagent.persona.to_dict()
        
        # Remove any function objects from tools that could cause serialization issues
        if memagent_dict.get("tools") and isinstance(memagent_dict["tools"], list):
            for tool in memagent_dict["tools"]:
                if "function" in tool and callable(tool["function"]):
                    del tool["function"]
        
        # Insert the document and let MongoDB generate _id automatically
        result = self.memagent_collection.insert_one(memagent_dict)
        
        # Add the generated _id to the response
        memagent_dict["_id"] = result.inserted_id

        return memagent_dict
    
    def update_memagent(self, memagent: "MemAgentModel") -> "MemAgentModel":
        """
        Update a memagent in the MongoDB database using _id field.
        """
        # Convert the MemAgentModel to a dictionary
        memagent_dict = memagent.model_dump()

        # Remove agent_id field since we only want to use _id
        agent_id = memagent_dict.pop("agent_id", None)
        
        # Convert persona to a serializable format if it exists
        if memagent.persona:
            memagent_dict["persona"] = memagent.persona.to_dict()
        
        # Remove any function objects from tools that could cause serialization issues
        if memagent_dict.get("tools") and isinstance(memagent_dict["tools"], list):
            for tool in memagent_dict["tools"]:
                if "function" in tool and callable(tool["function"]):
                    del tool["function"]
        
        # Update the memagent in the MongoDB database using _id
        if agent_id and ObjectId.is_valid(agent_id):
            self.memagent_collection.update_one(
                {"_id": ObjectId(agent_id)}, 
                {"$set": memagent_dict}
            )
        
        return memagent_dict

    
    def retrieve_memagent(self, agent_id: str) -> "MemAgentModel":
        """
        Retrieve a memagent from the MongoDB database using _id field.
        
        Parameters:
        -----------
        agent_id : str
            The agent ID to retrieve (MongoDB _id).
        
        Returns:
        --------
        MemAgentModel
            The retrieved memagent.
        """
        # Get the document from MongoDB using _id
        try:
            if ObjectId.is_valid(agent_id):
                document = self.memagent_collection.find_one({"_id": ObjectId(agent_id)}, {"embedding": 0})            
            else:
                return None
        except Exception:
            return None
        
        if not document:
            return None
        
        # Create a new MemAgent with data from the document
        # Use the MongoDB _id as agent_id since we no longer store agent_id field
        memagent = MemAgentModel(
            instruction=document.get("instruction"),
            application_mode=document.get("application_mode", "assistant"),
            max_steps=document.get("max_steps"),
            memory_ids=document.get("memory_ids") or [],
            agent_id=str(document.get("_id")),
            tools=document.get("tools"),
            long_term_memory_ids=document.get("long_term_memory_ids"),
            memory_provider=self
        )
        
        # Construct persona if present in the document
        if document.get("persona"):
            persona_data = document.get("persona")
            # Handle role as a string by matching it to a RoleType enum
            role_str = persona_data.get("role")
            role = None
            
            # Match the string role to a RoleType enum
            for role_type in RoleType:
                if role_type.value == role_str:
                    role = role_type
                    break
            
            # If no matching enum is found, default to GENERAL
            if role is None:
                role = RoleType.GENERAL
                
            memagent.persona = Persona(
                name=persona_data.get("name"),
                role=role,  # Pass the RoleType enum instead of string
                goals=persona_data.get("goals"),
                background=persona_data.get("background"),
                persona_id=persona_data.get("persona_id")
            )

        return memagent
    

    
    def list_memagents(self) -> List["MemAgentModel"]:
        """
        List all memagents in the MongoDB database.
        
        Returns:
        --------
        List[MemAgentModel]
            The list of memagents.
        """
        
        documents = list(self.memagent_collection.find({}, {"embedding": 0}))        
        agents = []
        
        for doc in documents:
            # Use the MongoDB _id as agent_id since we no longer store agent_id field
            agent = MemAgentModel(
                instruction=doc.get("instruction"),
                application_mode=doc.get("application_mode", "assistant"),
                max_steps=doc.get("max_steps"),
                memory_ids=doc.get("memory_ids") or [],
                agent_id=str(doc.get("_id")),
                tools=doc.get("tools"),  # Include tools from document
                long_term_memory_ids=doc.get("long_term_memory_ids"),
                memory_provider=self
            )
            
            # Construct persona if present in the document
            if doc.get("persona"):
                persona_data = doc.get("persona")
                # Handle role as a string by matching it to a RoleType enum
                role_str = persona_data.get("role")
                role = None
                
                # Match the string role to a RoleType enum
                for role_type in RoleType:
                    if role_type.value == role_str:
                        role = role_type
                        break
                
                # If no matching enum is found, default to GENERAL
                if role is None:
                    role = RoleType.GENERAL
                    
                agent.persona = Persona(
                    name=persona_data.get("name"),
                    role=role,  # Pass the RoleType enum instead of string
                    goals=persona_data.get("goals"),
                    background=persona_data.get("background"),
                    persona_id=persona_data.get("persona_id")
                )
                
            agents.append(agent)
            
        return agents

    
    def update_memagent_memory_ids(self, agent_id: str, memory_ids: List[str]) -> bool:
        """
        Update the memory_ids of a memagent in the memory provider using _id field.

        Parameters:
        -----------
        agent_id : str
            The id of the memagent to update (MongoDB _id).
        memory_ids : List[str]
            The list of memory_ids to update.

        Returns:
        --------
        bool
            True if update was successful, False otherwise.
        """
        try:
            if ObjectId.is_valid(agent_id):
                result = self.memagent_collection.update_one(
                    {"_id": ObjectId(agent_id)}, 
                    {"$set": {"memory_ids": memory_ids}}
                )
                return result.modified_count > 0
            else:
                return False
        except Exception:
            return False
    
    def delete_memagent_memory_ids(self, agent_id: str) -> bool:
        """
        Delete the memory_ids of a memagent in the memory provider.

        Parameters:
        -----------
        agent_id : str
            The id of the memagent to update (MongoDB _id).

        Returns:
        --------
        bool
            True if deletion was successful, False otherwise.
        """
        try:
            if ObjectId.is_valid(agent_id):
                result = self.memagent_collection.update_one(
                    {"_id": ObjectId(agent_id)}, 
                    {"$unset": {"memory_ids": []}}
                )
                return result.modified_count > 0
            else:
                return False
        except Exception:
            return False
    
    def delete_memagent(self, agent_id: str, cascade: bool = False) -> bool:
        """
        Delete a memagent from the memory provider by id.

        Parameters:
        -----------
        agent_id : str
            The id of the memagent to delete.
        cascade : bool
            Whether to cascade the deletion of the memagent. This deletes all the memory units associated with the memagent by deleting the memory_ids and their corresponding memory store in the memory provider.

        Returns:
        --------
        bool
            True if deletion was successful, False otherwise.
        """
        if cascade:
            # Retrieve the memagent
            memagent = self.retrieve_memagent(agent_id)

            if memagent is None:
                raise ValueError(f"MemAgent with id {agent_id} not found")
            
            # Delete all the memory units associated with the memagent by deleting the memory_ids and their corresponding memory store in the memory provider.
            for memory_id in memagent.memory_ids:
                # Loop through all the memory stores and delete records with the memory_ids
                for memory_type in MemoryType:
                    self._delete_memory_units_by_memory_id(memory_id, memory_type)
        else:
            try:
                if ObjectId.is_valid(agent_id):
                    result = self.memagent_collection.delete_one({"_id": ObjectId(agent_id)})
                    return result.deleted_count > 0
                else:
                    return False
            except Exception:
                return False

        return True
    
    def _delete_memory_units_by_memory_id(self, memory_id: str, memory_type: MemoryType):
        """
        Delete all the memory units associated with the memory_id.

        Parameters:
        -----------
        memory_id : str
            The id of the memory to delete.
        memory_type : MemoryType
            The type of memory to delete.

        Returns:
        --------
        bool
            True if deletion was successful, False otherwise.
        """
        if memory_type == MemoryType.CONVERSATION_MEMORY:
            self.conversation_memory_collection.delete_many({"memory_id": memory_id})

        elif memory_type == MemoryType.WORKFLOW_MEMORY:
            self.workflow_memory_collection.delete_many({"memory_id": memory_id})
        elif memory_type == MemoryType.SHORT_TERM_MEMORY:
            self.short_term_memory_collection.delete_many({"memory_id": memory_id})
        elif memory_type == MemoryType.LONG_TERM_MEMORY:
            self.long_term_memory_collection.delete_many({"memory_id": memory_id})
        elif memory_type == MemoryType.PERSONAS:
            self.persona_collection.delete_many({"memory_id": memory_id})
        elif memory_type == MemoryType.TOOLBOX:
            self.toolbox_collection.delete_many({"memory_id": memory_id})
        elif memory_type == MemoryType.MEMAGENT:
            self.memagent_collection.delete_many({"memory_id": memory_id})
                

    def _setup_vector_search_index(self, collection, index_name="vector_index", memory_store: bool = False):
        """
        Setup a vector search index for a MongoDB collection and wait for it to become queryable.

        Args:
        collection: MongoDB collection object
        index_name: Name of the index (default: "vector_index")
        memory_store: Whether to add the memory_id field to the index (default: False)
        """

        # Define the index definition
        vector_index_definition = {
            "fields": [
                {
                    "type": "vector",
                    "path": "embedding",
                    # Dynamic dimensions based on the configured embedding provider
                    "numDimensions": self._get_embedding_dimensions_safe(),
                    "similarity": "cosine",
                }
            ]
        }

        # If the memory store is true, then we add the memory_id field to the index
        # This is used to prefilter the memory units by memory_id
        # useful to narrow the scope of your semantic search and ensure that not all vectors are considered for comparison. 
        # It reduces the number of documents against which to run similarity comparisons, which can decrease query latency and increase the accuracy of search results.
        if memory_store:
            vector_index_definition["fields"].append({
                "type": "filter",
                "path": "memory_id",
            })

        new_vector_search_index_model = SearchIndexModel(
            definition=vector_index_definition, name=index_name, type="vectorSearch"
        )

        # Create the new index
        try:
            result = collection.create_search_index(model=new_vector_search_index_model)

            
            # Wait for the index to become queryable using polling mechanism
            self._wait_for_index_ready(collection, result, index_name)
            
            return result

        except Exception as e:
            return None

    def _wait_for_index_ready(self, collection, index_name_result, display_name="vector_index"):
        """
        Wait for a MongoDB Atlas search index to become queryable using polling.
        
        Args:
        collection: MongoDB collection object
        index_name_result: The name/result returned from create_search_index
        display_name: Human-readable name for logging (default: "vector_index")
        """

        
        # Define predicate function to check if index is queryable
        predicate = lambda index: index.get("queryable") is True
        
        while True:
            try:
                # List search indexes and find the one we just created
                indices = list(collection.list_search_indexes(index_name_result))
                
                # Check if the index exists and is queryable
                if indices and predicate(indices[0]):
                    break
                    
                # Wait 5 seconds before checking again
                time.sleep(5)
                
            except Exception as e:
                # Continue polling even if there's an error
                time.sleep(5)
        
    def _ensure_vector_index(self, collection, index_name="vector_index", memory_store: bool = False):
        """
        Ensure a vector search index exists for the collection. If it doesn't exist, create it and wait for it to be ready.
        
        Args:
        collection: MongoDB collection object
        index_name: Name of the index (default: "vector_index")
        memory_store: Whether to add the memory_id field to the index (default: False)
        """
        search_indexes = list(collection.list_search_indexes())
        has_vector_index = any(index.get("name") == index_name and index.get("type") == "vectorSearch" for index in search_indexes)
        
        if not has_vector_index:

            self._setup_vector_search_index(collection, index_name, memory_store)
        else:
            pass  # Index already exists

    def _ensure_semantic_cache_vector_index(self) -> None:
        """
        Ensure vector index exists for semantic cache collection with correct field name.
        """
        collection = self.semantic_cache_collection
        index_name = "vector_index"
        
        # Check if vector index already exists and has correct definition
        search_indexes = list(collection.list_search_indexes())
        existing_index = None
        for index in search_indexes:
            if index.get("name") == index_name and index.get("type") == "vectorSearch":
                existing_index = index
                break
        
        # Check if index exists and has all required filter fields
        has_correct_index = False
        if existing_index:
            fields = existing_index.get("definition", {}).get("fields", [])
            filter_paths = {field.get("path") for field in fields if field.get("type") == "filter"}
            required_filters = {"agent_id", "memory_id", "session_id"}
            has_correct_index = required_filters.issubset(filter_paths)
            
        # If index exists but has wrong definition, log warning but don't recreate
        if existing_index and not has_correct_index:
            logger.warning(f"Vector index '{index_name}' exists but has incomplete filter definition. "
                          f"Expected filters: agent_id, memory_id, session_id. "
                          f"To fix this, manually drop the index in MongoDB Atlas and restart the application.")
                
        has_vector_index = existing_index is not None  # Use existing index even if definition is incomplete
        
        if not has_vector_index:
            logger.info(f"Creating semantic cache vector index with filters: agent_id, memory_id, session_id")
            
            try:
                # Get embedding dimensions
                dimensions = self._get_embedding_dimensions_safe()
                logger.info(f"Using embedding dimensions: {dimensions}")
                
                # Create vector index definition for embedding field
                vector_index_definition = {
                    "fields": [
                        {
                            "type": "vector",
                            "path": "embedding",  # Standard embedding field name
                            "numDimensions": dimensions,
                            "similarity": "cosine",
                        },
                        {
                            "type": "filter", 
                            "path": "agent_id",  # Filter by agent_id
                        },
                        {
                            "type": "filter", 
                            "path": "memory_id",  # Filter by memory_id
                        },
                        {
                            "type": "filter", 
                            "path": "session_id",  # Filter by session_id
                        }
                    ]
                }
                
                new_vector_search_index_model = SearchIndexModel(
                    definition=vector_index_definition, 
                    name=index_name, 
                    type="vectorSearch"
                )
                
                logger.info(f"Creating vector search index '{index_name}' for semantic cache...")
                result = collection.create_search_index(model=new_vector_search_index_model)
                
                # Wait for the index to become queryable
                logger.info(f"Waiting for index '{index_name}' to become ready...")
                self._wait_for_index_ready(collection, result, index_name)
                
                logger.info(f" Vector index '{index_name}' for semantic cache is ready!")
                return result
                
            except Exception as e:
                logger.error(f" Failed to create semantic cache vector index: {e}")
                raise RuntimeError(f"Could not create semantic cache vector index: {e}")
        else:
            logger.info(f" Vector index '{index_name}' already exists and has correct definition")

    def close(self) -> None:
        """Close the connection to MongoDB."""
        self.client.close()