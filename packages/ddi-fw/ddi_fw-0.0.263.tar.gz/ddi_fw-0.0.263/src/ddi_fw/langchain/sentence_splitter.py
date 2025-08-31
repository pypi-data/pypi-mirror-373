from typing import List
import nltk
from nltk import sent_tokenize
from langchain_text_splitters.base import TextSplitter

nltk.download('punkt')

''' A text splitter that splits text into sentences using NLTK's sentence tokenizer.'''
class SentenceSplitter(TextSplitter):
    def split_text(self, text: str) -> List[str]:
        return sent_tokenize(text)


''' A text splitter that does not split the text at all, returning the entire text as a single chunk.'''
class PassthroughTextSplitter(TextSplitter):
    def split_text(self, text: str) -> List[str]:
        return [text]