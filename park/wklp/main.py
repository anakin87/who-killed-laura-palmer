from fastapi import FastAPI, Depends
from haystack.document_stores import FAISSDocumentStore
from haystack.nodes import DensePassageRetriever, FARMReader
from haystack.pipelines import ExtractiveQAPipeline
from pydantic import BaseModel
from diskcache import Cache

import logging
import time

from utils import check_authentication, set_logger


class QueryRequest(BaseModel):
    query: str
    params: dict = {"Retriever": {"top_k": 7}, 
                    "Reader": {"top_k": 5}}

set_logger()
# start a disk cache
cache = Cache('./cache', size_limit=10*2**30)

# load document store, retriever, reader and create pipeline
document_store = FAISSDocumentStore(
    faiss_index_path='./index/my_faiss_index.faiss',
    faiss_config_path='./index/my_faiss_index.json')
logging.info('Index size: {document_store.get_document_count()}')

retriever = DensePassageRetriever(document_store=document_store,
                                  query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
                                  passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base",
                                  max_seq_len_query=64,
                                  max_seq_len_passage=256,
                                  batch_size=16,
                                  use_gpu=False,
                                  embed_title=True,
                                  use_fast_tokenizers=True)
reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2-distilled", use_gpu=False)
pipeline = ExtractiveQAPipeline(reader, retriever)



app = FastAPI(title="WKLP API",
              description="""WKLP API""")


@app.get("/initialized", dependencies=[Depends(check_authentication)])
def check_status() -> bool:
    """
    This endpoint can be used during startup to understand if the 
    server is ready to take any requests, or is still loading.
    The recommended approach is to call this endpoint with a short timeout,
    like 500ms, and in case of no reply, consider the server busy.
    """
    return True

@app.post("/query", dependencies=[Depends(check_authentication)])
# since our index is fixed and the following method is expensive,
# we decide to cache it
@cache.memoize()
def query (query_request: QueryRequest) -> dict:
    """
    Runs the query and returns the response
    """
    start_time=time.time()
    query = query_request.query
    params = query_request.params
    result = pipeline.run(query, params=params)
    end_time=time.time()
    logging.info(f'inference time: {end_time - start_time}')
    return result