# inspired by https://github.com/deepset-ai/haystack/blob/master/ui/webapp.py

import time
import streamlit as st
import logging
from json import JSONDecodeError
from markdown import markdown
from annotated_text import annotation
from urllib.parse import unquote
import random

from app_utils.backend_utils import load_questions, query
from app_utils.frontend_utils import (set_state_if_absent, reset_results, 
    SIDEBAR_STYLE, TWIN_PEAKS_IMG_SRC, LAURA_PALMER_IMG_SRC, SPOTIFY_IFRAME)
from app_utils.config import RETRIEVER_TOP_K, READER_TOP_K, LOW_RELEVANCE_THRESHOLD

def main():
    questions = load_questions()

    # Persistent state
    set_state_if_absent('question', "Where is Twin Peaks?")
    set_state_if_absent('answer', '')
    set_state_if_absent('results', None)
    set_state_if_absent('raw_json', None)
    set_state_if_absent('random_question_requested', False)

    ## SIDEBAR
    st.markdown(SIDEBAR_STYLE, unsafe_allow_html=True)
    st.sidebar.header("Who killed Laura Palmer?")
    st.sidebar.image(TWIN_PEAKS_IMG_SRC)
    st.sidebar.markdown(f"""
        <p align="center"><b>Twin Peaks Question Answering system</b></p>
        <div class="haystack-footer">
        <p><a href="https://github.com/anakin87/who-killed-laura-palmer">GitHub</a> - 
        Built with <a href="https://github.com/deepset-ai/haystack/">Haystack</a><br/>
        <small>Data crawled from <a href="https://twinpeaks.fandom.com/wiki/Twin_Peaks_Wiki">
        Twin Peaks Wiki</a>.</small>       
        </p><img src = '{LAURA_PALMER_IMG_SRC}'/><br/></div>
        """, unsafe_allow_html=True)
    # spotify webplayer
    st.sidebar.markdown(SPOTIFY_IFRAME, unsafe_allow_html=True)

    ## MAIN CONTAINER
    st.write("# Who killed Laura Palmer?")
    st.write("### The first Twin Peaks Question Answering system!")
    st.markdown("""
    Ask any question about [Twin Peaks]
    (https://twinpeaks.fandom.com/wiki/Twin_Peaks) 
    and see if the AI ​​can find an answer...

    *Note: do not use keywords, but full-fledged questions.*
    """)
    # Search bar
    question = st.text_input("", value=st.session_state.question,
                             max_chars=100, on_change=reset_results)
    col1, col2 = st.columns(2)
    col1.markdown(
        "<style>.stButton button {width:100%;}</style>", unsafe_allow_html=True)
    col2.markdown(
        "<style>.stButton button {width:100%;}</style>", unsafe_allow_html=True)
    # Run button
    run_pressed = col1.button("Run")
    # Random question button
    if col2.button("Random question"):
        reset_results()
        question = random.choice(questions)
        # Avoid picking the same question twice (the change is not visible on the UI)
        while question == st.session_state.question:
            question = random.choice(questions)
        st.session_state.question = question
        st.session_state.random_question_requested = True
        # Re-runs the script setting the random question as the textbox value
        # Unfortunately necessary as the Random Question button is _below_ the textbox
        raise st.script_runner.RerunException(
            st.script_request_queue.RerunData(None))
    else:
        st.session_state.random_question_requested = False
    run_query = (run_pressed or question != st.session_state.question) \
        and not st.session_state.random_question_requested

    # Get results for query
    if run_query and question:
        time_start = time.time()
        reset_results()
        st.session_state.question = question
        with st.spinner("🧠 &nbsp;&nbsp; Performing neural search on documents..."):
            try:
                st.session_state.results = query(
                    question, RETRIEVER_TOP_K, READER_TOP_K)
                time_end = time.time()
                print(f'elapsed time: {time_end - time_start}')
            except JSONDecodeError as je:
                st.error(
                    "👓 &nbsp;&nbsp; An error occurred reading the results. Is the document store working?")
                return
            except Exception as e:
                logging.exception(e)
                st.error("🐞 &nbsp;&nbsp; An error occurred during the request.")
                return

    # Display results
    if st.session_state.results:
        st.write("## Results:")
        alert_irrelevance = True
        if len(st.session_state.results['answers']) == 0:
            st.info("""🤔 &nbsp;&nbsp; Haystack is unsure whether any of 
    the documents contain an answer to your question. Try to reformulate it!""")

        for result in st.session_state.results['answers']:
            result = result.to_dict()
            if result["answer"]:
                if alert_irrelevance and result['score'] < LOW_RELEVANCE_THRESHOLD:
                    alert_irrelevance = False
                    st.write("""
                    <h4 style='color: darkred'>Attention, the 
                    following answers have low relevance:</h4>""",
                             unsafe_allow_html=True)

            answer, context = result["answer"], result["context"]
            start_idx = context.find(answer)
            end_idx = start_idx + len(answer)
            # Hack due to this bug: https://github.com/streamlit/streamlit/issues/3190
            st.write(markdown("- ..."+context[:start_idx] +
                    str(annotation(answer, "ANSWER", "#3e1c21", "white")) + 
                    context[end_idx:]+"..."), unsafe_allow_html=True)
            source = ""
            name = unquote(result['meta']['name']).replace('_', ' ')
            url = result['meta']['url']
            source = f"[{name}]({url})"
            st.markdown(
                f"**Score:** {result['score']:.2f} -  **Source:** {source}")

main()
