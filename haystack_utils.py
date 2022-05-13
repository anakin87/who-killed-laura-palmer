import shutil
from haystack.document_stores import FAISSDocumentStore
from haystack.nodes import EmbeddingRetriever
from haystack.pipelines import ExtractiveQAPipeline
from haystack.nodes import FARMReader
import streamlit as st

from config import (INDEX_DIR, RETRIEVER_MODEL, RETRIEVER_MODEL_FORMAT,
    READER_MODEL, READER_CONFIG_THRESHOLD, QUESTIONS_PATH)

def start_haystack():
    """
    load document store, retriever, reader and create pipeline
    """
    shutil.copy(f'{INDEX_DIR}/faiss_document_store.db', '.')
    document_store = FAISSDocumentStore(
        faiss_index_path=f'{INDEX_DIR}/my_faiss_index.faiss',
        faiss_config_path=f'{INDEX_DIR}/my_faiss_index.json')
    print(f'Index size: {document_store.get_document_count()}')
    
    retriever = EmbeddingRetriever(
        document_store=document_store,
        embedding_model=RETRIEVER_MODEL,
        model_format=RETRIEVER_MODEL_FORMAT
    )
    
    reader = FARMReader(model_name_or_path=READER_MODEL,
                        use_gpu=False,
                        confidence_threshold=READER_CONFIG_THRESHOLD)
    
    pipe = ExtractiveQAPipeline(reader, retriever)
    return pipe

def set_state_if_absent(key, value):
    if key not in st.session_state:
        st.session_state[key] = value

def load_questions():
    with open(QUESTIONS_PATH) as fin:
        questions = [line.strip() for line in fin.readlines()
                     if not line.startswith('#')]
    return questions            