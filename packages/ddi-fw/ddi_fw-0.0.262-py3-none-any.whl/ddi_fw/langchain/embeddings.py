import numpy as np
from transformers import AutoModel, AutoTokenizer
from sentence_transformers import SentenceTransformer
from typing import Any, List
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, ConfigDict, computed_field
from langchain.embeddings import SentenceTransformerEmbeddings
 

class PoolingStrategy():
    def __init__(self):
        pass

    def apply(self, embeddings: List[List[float]]):
        pass


class MeanPoolingStrategy(PoolingStrategy):
    def __init__(self):
        pass

    def apply(self, embeddings: List[List[float]]):
        return np.mean(embeddings, axis=0)


class SumPoolingStrategy(PoolingStrategy):
    def __init__(self):
        pass

    def apply(self, embeddings: List[List[float]]):
        return np.sum(embeddings, axis=0)


class SentenceTransformerDecorator(Embeddings):
    def __init__(self, model_name="all-MiniLM-L6-v2", **kwargs: Any):
        self.embeddings = SentenceTransformerEmbeddings(model_name=model_name, **kwargs)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.embeddings.embed_query(text)


class PretrainedEmbeddings(Embeddings):
    def __init__(self, model_name):
        self.model_name = model_name
        self.model = AutoModel.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.shape = self.model.get_input_embeddings().weight.shape

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        output_embeddings = []
        texts = list(map(lambda x: x.replace("\n", " "), texts))
        for text in texts:
            input_ids = self.tokenizer.encode(
                text, return_tensors='pt', padding=True)
            output_embeddings.append(self.model(
                input_ids).last_hidden_state.mean(dim=1))
        return output_embeddings

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]


class SBertEmbeddings(BaseModel, Embeddings):
    # class Config:
    #     arbitrary_types_allowed = True

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed = True,
        protected_namespaces=()
    )

    model_name:str

    @computed_field
    @property
    def model(self) -> SentenceTransformer:
        return SentenceTransformer(self.model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts).tolist()

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

# class EmbeddingGenerator(ABC):

#     def __init__(self):
#         self.shape = None

#     @abstractmethod
#     def generate(self, text):
#         pass

# # https://github.com/huggingface/transformers/issues/1791
# class PretrainedEmbeddingGenerator(EmbeddingGenerator):
#     def __init__(self, model_name, split_text=True):
#         self.model_name = model_name
#         self.model = AutoModel.from_pretrained(model_name)
#         self.tokenizer = AutoTokenizer.from_pretrained(model_name)
#         self.shape = self.model.get_input_embeddings().weight.shape
#         self.split_text = split_text

#     def generate(self, text):
#         if self.split_text:
#             sentences = sent_tokenize(text)
#             output_embeddings = None
#             for sentence in sentences:
#                 input_ids  = self.tokenizer.encode(sentence, return_tensors='pt', padding=True)
#                 if output_embeddings == None:
#                     output_embeddings = self.model(input_ids).last_hidden_state.mean(dim=1)
#                 else:
#                     output_embeddings += self.model(input_ids).last_hidden_state.mean(dim=1)
#             if output_embeddings == None:
#                 output_embeddings = torch.empty((1,self.model.get_input_embeddings().weight.shape[1]))
#         else:
#             encoded_input = self.tokenizer(text, return_tensors='pt')
#             input_ids = self.tokenizer.encode(text, add_special_tokens=True, max_length=self.tokenizer.model_max_length, return_tensors='pt')
#             # input_ids  = encoded_input.input_ids[:self.tokenizer.model_max_length]
#             output_embeddings = self.model(input_ids)
#             # output_embeddings = self.model(**encoded_input)
#             # sentence embedding
#             output_embeddings = output_embeddings.last_hidden_state.mean(dim=1)
#         return torch.flatten(output_embeddings).detach().numpy()


# class LLMEmbeddingGenerator(EmbeddingGenerator):
#     pass


# class SBertEmbeddingGenerator(PretrainedEmbeddingGenerator):
#     def __init__(self, model_name, split_text=True):
#         self.model = SentenceTransformer(model_name)
#         self.shape = self.model._modules['0'].get_word_embedding_dimension()
#         self.split_text = split_text

#     def generate(self, text):
#         if text == None or type(text) != str:
#             embeddings = None
#         else:
#             if self.split_text:
#                 sentences = sent_tokenize(text)
#                 embeddings = self.model.encode(sentences)
#             else:
#                 embeddings = self.model.encode(text)
#         return embeddings


# # NOT modelden input size'ı anlama,
# def create_embeddings_new(generator: EmbeddingGenerator, data, column, drop_column=True):
#     column_embeddings_dict = defaultdict(lambda: np.zeros(generator.shape))
#     for index, row in tqdm(data.iterrows()):
#         # if index == 10:
#         #   break
#         text = data[column][index]
#         embeddings = generator.generate(text)

#     # TODO benzer olan ilacın embedding değerini vererek dene
#         # embedding check none type
#         if embeddings is None or len(embeddings) == 0:
#             sum_of_embeddings = np.zeros(generator.shape)
#         else:
#             sum_of_embeddings = np.sum(embeddings, axis=0)
#         # column_embeddings_dict[row['id']] = sum_of_embeddings.reshape(1, -1) # 2d
#         column_embeddings_dict[row['id']] = sum_of_embeddings
#         # data.iloc[index][column+'_embedding']=sum_of_embeddings

#     data[column+'_embedding'] = pd.Series(column_embeddings_dict.values())
#     if (drop_column):
#         data.drop([column], axis=1, inplace=True)
#     # data[column+'_embedding'] = [column_embeddings_dict[row['name']] for index, row in data.iterrows()]
#     return column_embeddings_dict
