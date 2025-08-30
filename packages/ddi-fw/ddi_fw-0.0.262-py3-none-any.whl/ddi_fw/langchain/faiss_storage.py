import faiss
from langchain_text_splitters import TextSplitter
import pandas as pd
from uuid import uuid4
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from typing import Callable, List, Optional, Dict, Any, Type
from langchain_core.documents import Document
import numpy as np  # optional, if you're using NumPy vectors
from langchain_core.embeddings import Embeddings

from pydantic import BaseModel, Field
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from ddi_fw.utils import get_import
from langchain.document_loaders import DataFrameLoader
from collections import defaultdict

class BaseVectorStoreManager(BaseModel):
    embeddings: Optional[Embeddings] = None
    vector_store: Optional[VectorStore]|None = None

    class Config:
        arbitrary_types_allowed = True

    def initialize_embedding_dict(self, **kwargs):
        raise NotImplementedError("This method should be implemented by subclasses.")

    def generate_vector_store(self, docs):
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def save(self, path):
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def load(self, path):
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def as_dataframe(self, formatter_fn: Optional[Callable[[Document, np.ndarray], Dict[str, Any]]] = None) -> pd.DataFrame:
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    @staticmethod
    def get_persist_dir(base_dir, id ,suffix, config=None):
        raise NotImplementedError("Subclasses must implement get_persist_dir.")
     

class FaissVectorStoreManager(BaseVectorStoreManager):
    persist_directory: str = Field(default="./embeddings/faiss")
    index: Any = None
    vector_store: Optional[FAISS] | None = None
    text_splitter: Optional[TextSplitter] = None
    class Config:
        arbitrary_types_allowed = True
    # def generate_vector_store(self, docs):
    #     dimension = len(self.embeddings.embed_query("hello world"))
    #     self.index = faiss.IndexFlatL2(dimension)
    #     index_to_docstore_id = {}

    #     self.vector_store = FAISS(
    #         embedding_function=self.embeddings,
    #         index=self.index,
    #         docstore=InMemoryDocstore(),
    #         index_to_docstore_id=index_to_docstore_id,
    #     )

    #     uuids = [str(uuid4()) for _ in range(len(docs))]
    #     self.vector_store.add_documents(documents=docs, ids=uuids)
    
    @staticmethod
    def get_persist_dir(base_dir,id, suffix, config=None):
        return f"{base_dir}/faiss/{id}/{suffix}"
    
    def initialize_embedding_dict(self, **kwargs):
        """
        Initializes a dictionary where keys are types (e.g., 'description', 'indication'),
        and values are dictionaries mapping drugbank_ids to a list of their embeddings.

        Returns:
            dict: A dictionary with the structure {type: {drugbank_id: [embedding]}}.
        """
        self.load(self.persist_directory)
        # df = self.as_dataframe(formatter_fn=custom_formatter)
        df = self.as_dataframe(formatter_fn=custom_formatter)
        type_dict = defaultdict(lambda: defaultdict(list))

        grouped = df.groupby(['type', 'id'])['embedding'].apply(list)

        for (drug_type, id), embeddings in grouped.items():
            type_dict[drug_type][id] = embeddings

        return type_dict
    
    def generate_vector_store(self, docs, handle_empty='zero'):
        """
        Generate a FAISS vector store from documents.

        Parameters:
            docs (list[Document]): List of LangChain Document objects.
            handle_empty (str): How to handle empty docs. Options:
                - 'zero': assign zero-vector
                - 'skip': skip the document
                - 'error': raise ValueError
        """
        if self.embeddings is None:
            raise ValueError("Embeddings must be initialized before generating vector store.")
        # Step 1: Get embedding dimension from a sample input
        sample_embedding = self.embeddings.embed_query("hello world")
        dimension = len(sample_embedding)
        zero_vector = np.zeros(dimension, dtype=np.float32)

        self.index = faiss.IndexFlatL2(dimension)
        index_to_docstore_id = {}
        docstore = InMemoryDocstore()
        self.vector_store = FAISS(
            embedding_function=self.embeddings,
            index=self.index,
            docstore=docstore,
            index_to_docstore_id=index_to_docstore_id,
        )

        valid_docs = []
        valid_ids = []
        if self.text_splitter:
            docs = self.text_splitter.split_documents(docs)
            
        for doc in docs:
            content = doc.page_content if hasattr(doc, 'page_content') else ""
            if content and content.strip():
                valid_docs.append(doc)
                valid_ids.append(str(uuid4()))
            else:
                if handle_empty == 'skip':
                    continue
                elif handle_empty == 'zero':
                    # Assign zero vector manually
                    doc_id = str(uuid4())
                    index_to_docstore_id[len(docstore._dict)] = doc_id
                    docstore._dict[doc_id] = doc
                    self.index.add(np.array([zero_vector]))
                elif handle_empty == 'error':
                    raise ValueError("Document has empty or blank content.")
                else:
                    raise ValueError(f"Unknown handle_empty mode: {handle_empty}")

        # Step 2: Embed and add valid documents
        if valid_docs:
            self.vector_store.add_documents(documents=valid_docs, ids=valid_ids)
        elif handle_empty != 'zero':
            raise ValueError("No valid documents to embed.")

        print(f"✅ Vector store created with {self.index.ntotal} vectors.")
    
    def save(self, path):
        if self.vector_store:
            self.vector_store.save_local(path)
        else:
            raise ValueError("No vector store to save.")

    def load(self, path):
        #self.embeddings
        self.vector_store = FAISS.load_local(
            path, self.embeddings, allow_dangerous_deserialization=True
        )
        self.index = self.vector_store.index

    def as_dataframe(
		self,
		formatter_fn: Optional[Callable[[Document, np.ndarray], Dict[str, Any]]] = None
	) -> pd.DataFrame:
				
        if not self.index or not self.vector_store:
            raise ValueError("Index or vector store not initialized.")

        vector_dict = {}
        for i in range(self.index.ntotal):
            vector = self.index.reconstruct(i)
            doc_id = self.vector_store.index_to_docstore_id[i]
            document = self.vector_store.docstore.search(doc_id)

            if formatter_fn:
                item = formatter_fn(document, vector)
            else:
                item = {
                    "embedding": vector,
                    **document.metadata
                }

            vector_dict[i] = item

        return pd.DataFrame.from_dict(vector_dict, orient='index')

    def get_data(self, id):
        if not self.index or not self.vector_store:
            raise ValueError("Index or vector store not initialized.")

        vector = self.index.reconstruct(id)
        doc_id = self.vector_store.index_to_docstore_id[id]
        document = self.vector_store.docstore.search(doc_id)
        return {"doc_id": doc_id, "document": document, "vector": vector}

    def get_all_vectors(self):
        if not self.index:
            raise ValueError("Index not initialized.")
        return self.index.reconstruct_n(0, self.index.ntotal)

    def get_vector_by_id(self, id):
        if not self.index:
            raise ValueError("Index not initialized.")
        return self.index.reconstruct(id)
		
    def get_document_by_index(self,index):
        doc_id = self.vector_store.index_to_docstore_id[index]
        document = self.vector_store.docstore.search(doc_id)
        return document
    
    def get_similar_embeddings(self, embedding_list, k):
        num_vectors, dim = embedding_list.shape

        # 2. Normalize for cosine similarity
        faiss.normalize_L2(embedding_list)

        # 3. Build FAISS index
        index = faiss.IndexFlatIP(dim)
        index.add(embedding_list)

        # 4. Query top-k+1 to exclude self-match
        # k = 4  # Request top 4, so we can drop self and keep 3
        D, I = index.search(embedding_list, k+1)

        # 5. Prepare output arrays
        top_k_ids_list = []
        top_k_avg_embeddings = []

        # id_list = desc_df['drugbank_id'].tolist()

        for i in range(num_vectors):
            indices = I[i]
            
            # Exclude self (assume it's the first match)
            filtered = [idx for idx in indices if idx != i][:k]

            # top_ids = [id_list[j] for j in filtered]
            top_embeds = embedding_list[filtered]

            avg_embed = np.mean(top_embeds, axis=0) if len(top_embeds) > 0 else np.zeros(dim)

            # top_k_ids_list.append(top_ids)
            top_k_ids_list.append(filtered)
            top_k_avg_embeddings.append(avg_embed)
        return top_k_ids_list, top_k_avg_embeddings
    
    def get_similar_docs(self, embedding, filter, top_k = 3):
        # Perform similarity search
        results = self.vector_store.similarity_search_with_score_by_vector(
            embedding,
            k=top_k ,  # Fetch more in case original sneaks in
            filter=filter
        )

        # Extract top-k drugbank_ids
        # top_k_ids = [doc.metadata.get("drugbank_id") for doc, score in results[:top_k]]
        # return top_k_ids
        return results[:top_k]
		

def custom_formatter(document: Document, vector: np.ndarray) -> Dict[str, Any]:
    return {
        "id": document.metadata.get("id", None),
        "type": document.metadata.get("type", None),
        "embedding": vector
    }

def load_configuration(config_file):
    """
    Load the configuration from a JSON file.
    """
    import json
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config


# def generate_embeddings(
#     df,
#     vector_store_manager_type:Type[BaseVectorStoreManager], 
#     config_file,
#     new_model_names,
#     collections,
#     persist_directory="embeddings",
# ):
#     """
#     Generate embeddings for collections based on a configuration file.

#     collections: List of collections that contain metadata for embedding generation.
#     config_file: Path to the configuration file containing model settings.
#     new_model_names: List of model names to generate embeddings for.
#     vector_store_manager_type: Class type of the vector store manager (e.g., FaissVectorStoreManager or ChromaVectorStoreManager)
#     """
#     if not collections and not config_file:
#         raise ValueError("Either 'collections' or 'config_file' must be provided.")
#     if collections and config_file:
#         raise ValueError("Only one of 'collections' or 'config_file' should be provided.")
    
#     if not collections:
#         collections = load_configuration(config_file)

#     for collection_config in collections:
#         id = collection_config['id']
#         name = collection_config['name']

#         if name not in new_model_names:
#             continue

#         embedding_model_type = collection_config.get('embedding_model_type')
#         text_splitters_types = collection_config.get('text_splitters_types')
#         batch_size = collection_config.get('batch_size')
#         partial_df_size = collection_config.get('partial_dataframe_size')
#         columns = collection_config.get('columns')
#         page_content_columns = collection_config.get('page_content_columns')
#         persist_dir = f'{persist_directory}/{id}'

#         # Load embedding model
#         try:
#             model_kwargs = collection_config.get('model_kwargs')
#             model = get_import(embedding_model_type)(
#                 model_name=name, **model_kwargs)
#         except Exception as e:
#             raise Exception(f"Unknown embedding model: {embedding_model_type}") from e

#         # Load text splitters
#         text_splitters = []
#         text_splitters_suffixes = []
#         for text_splitter_type in text_splitters_types:
#             try:
#                 type_of_text_splitter = get_import(
#                     text_splitter_type.get("type"))
#                 kwargs = text_splitter_type.get("params")
#                 suffix = text_splitter_type.get("suffix")
#                 if kwargs:
#                     text_splitter = type_of_text_splitter(**kwargs)
#                 else:
#                     text_splitter = type_of_text_splitter()
#                 text_splitters.append(text_splitter)
#                 text_splitters_suffixes.append(suffix)
#             except Exception as e:
#                 raise Exception(f"Unknown text splitter: {text_splitter_type}") from e

#         for text_splitter, suffix in zip(text_splitters, text_splitters_suffixes):
#             print(f"{id}_{suffix}")

#             # Prepare manager parameters
#             manager_params = {
#                 "collection_name": f"{id}_{suffix}",
#                 "persist_directory": persist_dir,
#                 "embeddings": model,
#                 "text_splitter": text_splitter,
#                 "batch_size": batch_size
#             }

#             # Instantiate the manager class
#             vector_store_manager = vector_store_manager_type(**manager_params)

#             # Prepare documents
#             # You may need to use a DataFrameLoader or similar to convert df to LangChain Documents
#             loader = DataFrameLoader(
#                 data_frame=df, page_content_column=page_content_columns[0]
#             )
#             docs = loader.load()

#             # Generate vector store
#             vector_store_manager.generate_vector_store(docs)

#             # Optionally persist/save
#             vector_store_manager.save(persist_dir)

# persist_directory config'den alınsın
def generate_embeddings(
    docs,
    vector_store_manager_type:Type[BaseVectorStoreManager],
    config_file:Optional[str],
    new_model_names:Optional[List],
    collections:Optional[Dict],
    persist_directory="./embeddings",
):
    """
    Generate embeddings for collections based on a configuration file.

    collections: List of collections that contain metadata for embedding generation.
    config_file: Path to the configuration file containing model settings.
    new_model_names: List of model names to generate embeddings for.
    vector_store_manager_type: Class type of the vector store manager (e.g., FaissVectorStoreManager or ChromaVectorStoreManager)
    """
    if not collections and not config_file:
        raise ValueError("Either 'collections' or 'config_file' must be provided.")
    if collections and config_file:
        raise ValueError("Only one of 'collections' or 'config_file' should be provided.")

    if not collections:
        collections = load_configuration(config_file)
    if collections is None:
        raise ValueError("No collections found in the configuration file.")
    for collection_config in collections:
        id = collection_config['id']
        name = collection_config['name']
        if name not in new_model_names:
            continue
        embedding_model_type = collection_config.get('embedding_model_type')
        text_splitters_types = collection_config.get('text_splitters_types')
        batch_size = collection_config.get('batch_size')
        partial_df_size = collection_config.get('partial_dataframe_size')
        columns = collection_config.get('columns')
        page_content_columns = collection_config.get('page_content_columns')
        

        # Load embedding model
        try:
            model_kwargs = collection_config.get('model_kwargs')
            model = get_import(embedding_model_type)(
                model_name=name, **model_kwargs)
        except Exception as e:
            raise Exception(f"Unknown embedding model: {embedding_model_type}") from e

        # Load text splitters
        text_splitters = []
        text_splitters_suffixes = []
        for text_splitter_type in text_splitters_types:
            try:
                type_of_text_splitter = get_import(
                    text_splitter_type.get("type"))
                kwargs = text_splitter_type.get("params")
                suffix = text_splitter_type.get("suffix")
                if kwargs:
                    text_splitter = type_of_text_splitter(**kwargs)
                else:
                    text_splitter = type_of_text_splitter()
                text_splitters.append(text_splitter)
                text_splitters_suffixes.append(suffix)
            except Exception as e:
                raise Exception(f"Unknown text splitter: {text_splitter_type}") from e
        
        for text_splitter, suffix in zip(text_splitters, text_splitters_suffixes):
            print(f"{id}_{suffix}")
            # persist_dir = f'{persist_directory}/{id}/{suffix}'
            # persist_dir = f'{persist_directory}/{suffix}'
            persist_dir = vector_store_manager_type.get_persist_dir(persist_directory , id, suffix, collection_config)

            # Prepare manager parameters
            manager_params = {
                "collection_name": f"{id}_{suffix}",
                "persist_directory": persist_dir,
                "embeddings": model,
                "text_splitter": text_splitter,
                "batch_size": batch_size
            }

            # Instantiate the manager class
            vector_store_manager = vector_store_manager_type(**manager_params)

            # Generate vector store
            vector_store_manager.generate_vector_store(docs)

            # Optionally persist/save
            vector_store_manager.save(persist_dir)