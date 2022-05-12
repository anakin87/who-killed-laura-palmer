import os
import time
import streamlit as st
import subprocess
import sys
import logging
import pandas as pd
from json import JSONDecodeError
from pathlib import Path
from markdown import markdown
import random
from typing import List, Dict, Any, Tuple

from haystack.document_stores import ElasticsearchDocumentStore, FAISSDocumentStore
from haystack.nodes import EmbeddingRetriever
from haystack.pipelines import ExtractiveQAPipeline
from haystack.preprocessor.preprocessor import PreProcessor
from haystack.nodes import FARMReader, TransformersReader
from haystack.pipelines import ExtractiveQAPipeline
from annotated_text import annotation
import shutil

# FAISS index directory
INDEX_DIR = 'data/index'


# the following function is cached to make index and models load only at start
@st.cache(hash_funcs={"builtins.SwigPyObject": lambda _: None}, allow_output_mutation=True)
def start_haystack():
  """
  load document store, retriever, reader and create pipeline
  """
  shutil.copy(f'{INDEX_DIR}/faiss_document_store.db','.')
  document_store = FAISSDocumentStore(
      faiss_index_path=f'{INDEX_DIR}/my_faiss_index.faiss',
      faiss_config_path=f'{INDEX_DIR}/my_faiss_index.json')
  print (f'Index size: {document_store.get_document_count()}')  
  retriever = EmbeddingRetriever(
      document_store=document_store,
    embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1",
    model_format="sentence_transformers"
  )
  reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=True)
  pipe = ExtractiveQAPipeline(reader, retriever)
  return pipe  

def set_state_if_absent(key, value):
    if key not in st.session_state:
        st.session_state[key] = value

def get_backlink(result, ip) -> str:
    """
    Build URL from metadata and Google VM IP
    (quick and dirty)
    """
    meta = result['meta']
    fpath = meta['filepath'].rpartition('/')[-1]
    fname = fpath.rpartition('.')[0]
    return f'http://{ip}:8000/data/final/ner_html/{fname}.html'


def query(pipe, question):
    """Run query and get answers"""
    return (pipe.run(question, params={"Retriever": {"top_k": 10}, "Reader": {"top_k": 5}}), None)

def main():
    # st.set_page_config(page_title='Who killed Laura Palmer?',
    # page_icon="https://static.wikia.nocookie.net/twinpeaks/images/4/4a/Site-favicon.ico/revision/latest?cb=20210710003705")
    
    pipe=start_haystack()
    # my_ip=subprocess.run(['curl', 'ifconfig.me'], stdout=subprocess.PIPE).stdout.decode('utf-8')

    # Persistent state
    set_state_if_absent('question', "Where is Twin Peaks?")
    set_state_if_absent('answer', '')
    set_state_if_absent('results', None)
    set_state_if_absent('raw_json', None)
    set_state_if_absent('random_question_requested', False)

    # Small callback to reset the interface in case the text of the question changes
    def reset_results(*args):
        st.session_state.answer = None
        st.session_state.results = None
        st.session_state.raw_json = None


    # Title
    st.write("# Who killed Laura Palmer?")
    st.write("### The first Twin Peaks Question Answering system!")
    
    st.markdown("""<br/>
Ask any question on [Twin Peaks] (https://twinpeaks.fandom.com/wiki/Twin_Peaks) and see if the AI can find answer...!

*Note: do not use keywords, but full-fledged questions.*
""", unsafe_allow_html=True)

    # Sidebar
    st.sidebar.header("Who killed Laura Palmer?")   
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/it/3/39/Twin-peaks-1990.jpg")
    st.sidebar.markdown("<p align="center">#### Twin Peaks Question Answering system</p>", unsafe_allow_html=True)
    st.sidebar.markdown(f"""
    <style>
        a {{
            text-decoration: none;
        }}
        .haystack-footer {{
            text-align: center;
        }}
        .haystack-footer h4 {{
            margin: 0.1rem;
            padding:0;
        }}
        footer {{
            opacity: 0;
        }}
        .haystack-footer img {{
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 85%;
        }}
    </style>
    <div class="haystack-footer">
        <p>Get it on <a href="https://github.com/deepset-ai/haystack/">GitHub</a> &nbsp;&nbsp; - &nbsp;&nbsp;
        Built with <a href="https://github.com/deepset-ai/haystack/">Haystack</a><br/>
        <small>Data crawled from <a href="https://twinpeaks.fandom.com/wiki/Twin_Peaks_Wiki">Twin Peaks Wiki</a>.</small>       
    </p>
    <img src = 'https://static.wikia.nocookie.net/twinpeaks/images/e/ef/Laura_Palmer%2C_the_Queen_Of_Hearts.jpg'/>
    <br/>
    </div>
    """, unsafe_allow_html=True)

    # st.sidebar.image('https://static.wikia.nocookie.net/twinpeaks/images/e/ef/Laura_Palmer%2C_the_Queen_Of_Hearts.jpg', width=270) #use_column_width='always'
    song_i = random.randint(1,11)
    st.sidebar.audio(f'http://twinpeaks.narod.ru/Media/0{song_i}.mp3')    

    # Search bar
    question = st.text_input("",
        value=st.session_state.question,
        max_chars=100,
        #on_change=reset_results
    )
    col1, col2 = st.columns(2)
    col1.markdown("<style>.stButton button {width:100%;}</style>", unsafe_allow_html=True)
    col2.markdown("<style>.stButton button {width:100%;}</style>", unsafe_allow_html=True)

    # Run button
    run_pressed = col1.button("Run")
    
    run_query = (run_pressed or question != st.session_state.question) and not st.session_state.random_question_requested

    # Get results for query
    if run_query and question:
        reset_results()
        st.session_state.question = question

        with st.spinner(
            "🧠 &nbsp;&nbsp; Performing neural search on documents..."

        ):
            try:
                st.session_state.results, st.session_state.raw_json = query(pipe, question)
            except JSONDecodeError as je:
                st.error("👓 &nbsp;&nbsp; An error occurred reading the results. Is the document store working?")
                return
            except Exception as e:
                logging.exception(e)
                if "The server is busy processing requests" in str(e) or "503" in str(e):
                    st.error("🧑‍🌾 &nbsp;&nbsp; All our workers are busy! Try again later.")
                else:
                    st.error("🐞 &nbsp;&nbsp; An error occurred during the request.")
                return

    if st.session_state.results:
        st.write("## Results:")

        alert_irrelevance=True

        for count, result in enumerate(st.session_state.results['answers']):
            result=result.to_dict()
            if result["answer"]:
                if alert_irrelevance and result['score']<=0.40:
                    alert_irrelevance = False
                    st.write("<h3 style='color: red'>Attention, the following answers have low relevance:</h3>", unsafe_allow_html=True)

            answer, context = result["answer"], result["context"]
            #authors, title = result["meta"]["authors"], result["meta"]["title"]
            start_idx = context.find(answer)
            end_idx = start_idx + len(answer)
            #url = get_backlink(result, my_ip)
            # Hack due to this bug: https://github.com/streamlit/streamlit/issues/3190
            st.write(markdown("- ..."+context[:start_idx] + str(annotation(answer, "ANSWER", "#8ef")) + context[end_idx:]+"..."), unsafe_allow_html=True)
            #st.write(markdown(f"<a href='{url}'>{title} - <i>{authors}</i></a>"), unsafe_allow_html=True)
            #st.write(markdown(f"**Relevance:** {result['score']:.2f}"), unsafe_allow_html=True)

main()
