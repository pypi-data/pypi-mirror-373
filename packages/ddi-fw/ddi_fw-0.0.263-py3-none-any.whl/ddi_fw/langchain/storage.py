import json
from langchain.vectorstores import Chroma
# from langchain_community.vectorstores import Chroma
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_core.embeddings import Embeddings
import time


from langchain.docstore.document import Document

from langchain.document_loaders import DataFrameLoader

from langchain.text_splitter import TextSplitter
import numpy as np

# from langchain_community.document_loaders.hugging_face_dataset import HuggingFaceDatasetLoader
from ddi_fw.langchain.embeddings import SBertEmbeddings
from ddi_fw.utils import get_import


def load_configuration(config_file):
    """
    Load the configuration from a JSON file.
    """
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config


def split_dataframe(df, min_size=512):
    total_size = len(df)
    # If the dataframe is smaller than min_size, return the dataframe as a whole
    if total_size <= min_size:
        return [df]

    # List to store partial DataFrames
    partial_dfs = []
    start_idx = 0

    # Calculate the minimum number of chunks we need to ensure each chunk has at least min_size
    num_chunks = total_size // min_size
    remaining_rows = total_size
    # Split into chunks
    for i in range(num_chunks):
        # If there are fewer rows left than the size of the chunk, adjust the chunk size
        chunk_size = min_size
        if (remaining_rows - chunk_size) < min_size:
            chunk_size = remaining_rows  # Last chunk takes all remaining rows

        partial_dfs.append(df.iloc[start_idx:start_idx + chunk_size])

        # Update the start index and remaining rows
        start_idx += chunk_size
        remaining_rows -= chunk_size

    # If there are any remaining rows left after the loop, they should form the last chunk
    if remaining_rows > 0:
        partial_dfs.append(df.iloc[start_idx:start_idx + remaining_rows])

    return partial_dfs


def split_dataframe_indices(df, min_size=512):
    total_size = len(df)

    # If the dataframe is smaller than min_size, return the entire range
    if total_size <= min_size:
        return [(0, total_size - 1)]

    # List to store the start and end indices of each chunk
    chunk_indices = []
    start_idx = 0

    # Calculate the minimum number of chunks needed to ensure each chunk has at least min_size
    num_chunks = total_size // min_size
    remaining_rows = total_size

    # Split into chunks
    for i in range(num_chunks):
        chunk_size = min_size
        if (remaining_rows - chunk_size) < min_size:
            chunk_size = remaining_rows  # Last chunk takes all remaining rows

        # Calculate the ending index of the chunk (exclusive, hence chunk_size - 1)
        end_idx = start_idx + chunk_size - 1
        chunk_indices.append((start_idx, end_idx))

        # Update the start index and remaining rows
        start_idx += chunk_size
        remaining_rows -= chunk_size

    # If there are any remaining rows after the loop, they should form the last chunk
    if remaining_rows > 0:
        end_idx = start_idx + remaining_rows - 1
        chunk_indices.append((start_idx, end_idx))

    return chunk_indices


class DataFrameToVectorDB:
    def __init__(self,
                 collection_name,
                 persist_directory,
                 embeddings: Embeddings,
                 text_splitter: TextSplitter,
                 batch_size=1024):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embeddings = embeddings
        self.text_splitter = text_splitter
        self.batch_size = batch_size  # to store chunks partially
        self.vectordb = Chroma(collection_name=collection_name,
                               persist_directory=persist_directory,
                               embedding_function=embeddings)

    def __split_docs(self, documents):
        docs = self.text_splitter.split_documents(documents)
        return docs

    def __split_list(self, input_list, batch_size):
        # for i in range(0, len(input_list), batch_size):
        batch_size = len(input_list) if batch_size == None else batch_size
        for s, e in split_dataframe_indices(input_list, batch_size):
            yield input_list[s:e+1]

    def store_documents(self, df, columns, page_content_columns, partial_df_size=None):
        """
        Core function that processes the documents and adds them to the vector database.
        """
        for page_content_column in page_content_columns:
            copy_columns = columns.copy()
            copy_columns.append(page_content_column)
            col_df = df[copy_columns].copy()
            col_df.dropna(subset=[page_content_column], inplace=True)
            col_df['type'] = page_content_column  # Set the type column
            if partial_df_size:
                total = 0
                partial_dfs = split_dataframe(col_df, min_size=partial_df_size)
                for partial_df in partial_dfs:
                    # import torch

                    documents = []
                    loader = DataFrameLoader(
                        data_frame=partial_df, page_content_column=page_content_column)
                    loaded_docs = loader.load()
                    # print(loaded_docs)
                    documents.extend(self.__split_docs(loaded_docs))
                    split_docs_chunked = self.__split_list(
                        documents, self.batch_size)
                    for split_docs_chunk in split_docs_chunked:
                        print("entered chunks")
                        self.vectordb.add_documents(split_docs_chunk)
                        self.vectordb.persist()
                    total += len(partial_df)
                    print(f"{page_content_column}: {total}/{len(col_df)}")
                    # torch.cuda.empty_cache()
                    # time.sleep(30)  # The GPU will not be used during this period

                    # split_docs_chunked = self.__split_list(
                    #     loaded_docs, self.batch_size)
                    # print(f"Number of chunks: {len(split_docs_chunked)}")
                    # for split_docs_chunk in split_docs_chunked:
                    #     print(f"Split docs size: {len(split_docs_chunk)}")
                    #     self.vectordb.add_documents(split_docs_chunk)
                    #     self.vectordb.persist()
            else:
                documents = []
                print(col_df.shape)
                loader = DataFrameLoader(
                    data_frame=col_df, page_content_column=page_content_column)
                loaded_docs = loader.load()
                documents.extend(self.__split_docs(loaded_docs))
                print(f"Documents size: {len(loaded_docs)}")
                split_docs_chunked = self.__split_list(
                    documents, self.batch_size)
                for split_docs_chunk in split_docs_chunked:
                    # import torch
                    # torch.cuda.empty_cache()
                    self.vectordb.add_documents(split_docs_chunk)
                    self.vectordb.persist()
                    print(f"{page_content_column}, size:{len(split_docs_chunk)}")


# TODO name yerine ID kullanılacak
def generate_embeddings(df, config_file, new_model_names, collections=None, persist_directory="embeddings"):
    """
    Generate embeddings for collections based on a configuration file.

    collections: List of collections that contain metadata for embedding generation.
    config_file: Path to the configuration file containing model settings.
    new_model_names: List of model names to generate embeddings for.
    """
    # Load the configuration from the provided file
    if not collections:
        collections = load_configuration(config_file)

    # Process each collection
    for collection_config in collections:
        id = collection_config['id']
        name = collection_config['name']

        # Skip if the collection's name is not in the list of new model names
        if name not in new_model_names:
            continue

        # # Find the matching configuration for the collection
        # collection_config = next(
        #     (item for item in collections if item['id'] == id), None)

        # if not collection_config:
        #     print(f"Configuration for collection {id} not found.")
        #     continue

        embedding_model_type = collection_config.get('embedding_model_type')
        text_splitters_types = collection_config.get('text_splitters_types')
        batch_size = collection_config.get('batch_size')
        partial_df_size = collection_config.get('partial_dataframe_size')
        columns = collection_config.get('columns')
        page_content_columns = collection_config.get('page_content_columns')
        persist_directory = f'{persist_directory}/{id}'

        # Load the embedding model and text splitter dynamically
        print(f"Generating embeddings for {id} with model {name}...")

        # Assuming the classes for the embeddings and splitters are available
        try:
            model_kwargs = collection_config.get('model_kwargs')
            model = get_import(embedding_model_type)(
                model_name=name, **model_kwargs)
        except:
            # print(f"Unknown embedding model: {embedding_model_type}")
            raise Exception(f"Unknown embedding model: {embedding_model_type}")

        text_splitters = []
        text_splitters_suffixes = []
        for text_splitter_type in text_splitters_types:
            try:
                type_of_text_splitter = get_import(
                    text_splitter_type.get("type"))
                kwargs = text_splitter_type.get("params")
                suffix = text_splitter_type.get("suffix")
                if kwargs:
                    text_splitter = type_of_text_splitter(
                        **kwargs)
                else:
                    text_splitter = type_of_text_splitter()
                text_splitters.append(text_splitter)
                text_splitters_suffixes.append(suffix)
            except:
                print(f"Unknown text splitter: {text_splitter_type}")
                raise Exception(f"Unknown text splitter: {text_splitter_type}")

        for text_splitter, suffix in zip(text_splitters, text_splitters_suffixes):
            print(f"{id}_{suffix}")
            to_vector_db = DataFrameToVectorDB(collection_name=f"{id}_{suffix}",
                                               persist_directory=persist_directory,
                                               embeddings=model,
                                               text_splitter=text_splitter,
                                               batch_size=batch_size)
            to_vector_db.store_documents(
                df, columns, page_content_columns, partial_df_size=partial_df_size)
