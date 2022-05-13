import shutil
from haystack.document_stores import FAISSDocumentStore
from haystack.nodes import EmbeddingRetriever
from haystack.pipelines import ExtractiveQAPipeline
from haystack.nodes import FARMReader
import streamlit as st

from config import (INDEX_DIR, RETRIEVER_MODEL, RETRIEVER_MODEL_FORMAT,
    READER_MODEL, READER_CONFIG_THRESHOLD, QUESTIONS_PATH)

@st.cache(hash_funcs={"builtins.SwigPyObject": lambda _: None},
          allow_output_mutation=True)
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

@st.cache()
def load_questions():
    with open(QUESTIONS_PATH) as fin:
        questions = [line.strip() for line in fin.readlines()
                     if not line.startswith('#')]
    return questions

# # the following function is a wrapper for start_haystack,
# # which loads document store, retriever, reader and creates pipeline.
# # cached to make index and models load only at start
# @st.cache(hash_funcs={"builtins.SwigPyObject": lambda _: None},
#           allow_output_mutation=True)
# def start_app():
#     return start_haystack()


# @st.cache()
# def load_questions_wrapper():
#     return load_questions()

pipe = start_haystack()

# the pipeline is not included as parameter of the following function,
# because it is difficult to cache
@st.cache(persist=True, allow_output_mutation=True)
def query(question: str, retriever_top_k: int = 10, reader_top_k: int = 5):
    """Run query and get answers"""
    params = {"Retriever": {"top_k": retriever_top_k},
              "Reader": {"top_k": reader_top_k}}
    results = pipe.run(question, params=params)
    return results                