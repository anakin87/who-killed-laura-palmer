import os
import sys

import logging
import pandas as pd
from json import JSONDecodeError
from pathlib import Path
import streamlit as st
from annotated_text import annotation
from markdown import markdown
import random

from utils import haystack_is_ready, query, send_feedback, upload_doc, haystack_version, get_backlink


# Adjust to a question that you would like users to see in the search bar when they load the UI:
DEFAULT_QUESTION_AT_STARTUP = os.getenv("DEFAULT_QUESTION_AT_STARTUP", "Who is Laura Palmer?")
DEFAULT_ANSWER_AT_STARTUP = os.getenv("DEFAULT_ANSWER_AT_STARTUP", "")

# Sliders
DEFAULT_DOCS_FROM_RETRIEVER = int(os.getenv("DEFAULT_DOCS_FROM_RETRIEVER", 3))
DEFAULT_NUMBER_OF_ANSWERS = int(os.getenv("DEFAULT_NUMBER_OF_ANSWERS", 3))

top_k_retriever=7
top_k_reader=5

# Labels for the evaluation
EVAL_LABELS = os.getenv("EVAL_FILE", Path(__file__).parent / "eval_labels_example.csv")

# Whether the file upload should be enabled or not
DISABLE_FILE_UPLOAD = True


def set_state_if_absent(key, value):
    if key not in st.session_state:
        st.session_state[key] = value

def main():

    st.set_page_config(page_title='Who killed Laura Palmer?', page_icon="https://haystack.deepset.ai/img/HaystackIcon.png")

    # Persistent state
    set_state_if_absent('question', DEFAULT_QUESTION_AT_STARTUP)
    set_state_if_absent('answer', DEFAULT_ANSWER_AT_STARTUP)
    set_state_if_absent('results', None)
    set_state_if_absent('raw_json', None)
    set_state_if_absent('random_question_requested', False)


    # Small callback to reset the interface in case the text of the question changes
    def reset_results(*args):
        st.session_state.answer = None
        st.session_state.results = None
        st.session_state.raw_json = None

#     page_bg_img = """
#     <style>
#     .reportview-container {
#         background: url("https://upload.wikimedia.org/wikipedia/it/3/39/Twin-peaks-1990.jpg")
#     }
#    .sidebar .sidebar-content {
#         background: url("https://upload.wikimedia.org/wikipedia/it/3/39/Twin-peaks-1990.jpg")
#     }
#     </style>

#     """

    # st.markdown(page_bg_img, unsafe_allow_html=True)
    # st.image("https://upload.wikimedia.org/wikipedia/it/3/39/Twin-peaks-1990.jpg")

    # Title
    st.write("# Who killed Laura Palmer?")
    st.write("### The first Twin Peaks Question Answering system!")
    
    st.markdown("""<br/>
Ask any question on Twin Peaks and see if the systsem can find the correct answer to your query!

*Note: do not use keywords, but full-fledged questions.*
""", unsafe_allow_html=True)

    # Sidebar
    
    st.sidebar.header("Who killed Laura Palmer?")
    
    
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/it/3/39/Twin-peaks-1990.jpg")
    st.sidebar.markdown("#### Twin Peaks Question Answering system")
    # top_k_reader = st.sidebar.slider(
    #     "Max. number of answers",
    #     min_value=1,
    #     max_value=10,
    #     value=DEFAULT_NUMBER_OF_ANSWERS,
    #     step=1,
    #     on_change=reset_results)
    # top_k_retriever = st.sidebar.slider(
    #     "Max. number of documents from retriever",
    #     min_value=1,
    #     max_value=10,
    #     value=DEFAULT_DOCS_FROM_RETRIEVER,
    #     step=1,
    #     on_change=reset_results)
    # eval_mode = st.sidebar.checkbox("Evaluation mode")
    # debug = st.sidebar.checkbox("Show debug info")

    # # File upload block
    # if not DISABLE_FILE_UPLOAD:
    #     st.sidebar.write("## File Upload:")
    #     data_files = st.sidebar.file_uploader("", type=["pdf", "txt", "docx"], accept_multiple_files=True)
    #     for data_file in data_files:
    #         # Upload file
    #         if data_file:
    #             raw_json = upload_doc(data_file)
    #             st.sidebar.write(str(data_file.name) + " &nbsp;&nbsp; ✅ ")
    #             if debug:
    #                 st.subheader("REST API JSON response")
    #                 st.sidebar.write(raw_json)

    # hs_version = ""
    # try:
    #     hs_version = f" <small>(v{haystack_version()})</small>"
    # except Exception:
    #     pass

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

    # Load csv into pandas dataframe
    try:
        df = pd.read_csv(EVAL_LABELS, sep=";")
    except Exception:
        st.error(f"The eval file was not found. Please check the demo's [README](https://github.com/deepset-ai/haystack/tree/master/ui/README.md) for more information.")
        sys.exit(f"The eval file was not found under `{EVAL_LABELS}`. Please check the README (https://github.com/deepset-ai/haystack/tree/master/ui/README.md) for more information.")

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

    # Get next random question from the CSV
    if col2.button("Random question"):
        reset_results()
        new_row = df.sample(1)
        while new_row["Question Text"].values[0] == st.session_state.question:  # Avoid picking the same question twice (the change is not visible on the UI)
            new_row = df.sample(1)
        st.session_state.question = new_row["Question Text"].values[0]
        st.session_state.answer = new_row["Answer"].values[0]
        st.session_state.random_question_requested = True
        # Re-runs the script setting the random question as the textbox value
        # Unfortunately necessary as the Random Question button is _below_ the textbox
        raise st.script_runner.RerunException(st.script_request_queue.RerunData(None))
    else:
        st.session_state.random_question_requested = False
    
    run_query = (run_pressed or question != st.session_state.question) and not st.session_state.random_question_requested
    
    # Check the connection
    with st.spinner("⌛️ &nbsp;&nbsp; Haystack is starting..."):
        if not haystack_is_ready():
            st.error("🚫 &nbsp;&nbsp; Connection Error. Is Haystack running?")
            run_query = False
            reset_results()

    # Get results for query
    if run_query and question:
        reset_results()
        st.session_state.question = question

        with st.spinner(
            "🧠 &nbsp;&nbsp; Performing neural search on documents... \n "
            "The response may be slow because the system is running on CPU. \n"
            "If you want to support and speed up this site, please contact me on Github. "
        ):
            try:
                st.session_state.results, st.session_state.raw_json = query(question, top_k_reader=top_k_reader,
                                                                            top_k_retriever=top_k_retriever)
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
        eval_mode=False

        # Show the gold answer if we use a question of the given set
        if eval_mode and st.session_state.answer:
            st.write("## Correct answer:")
            st.write(st.session_state.answer)

        st.write("## Results:")

        alert_irrelevance=True

        for count, result in enumerate(st.session_state.results):
            if result["answer"]:
                if alert_irrelevance and result['relevance']<=30:
                    alert_irrelevance = False
                    st.write("<h3 style='color: red'>Attention, the following answers have low relevance:</h3>", unsafe_allow_html=True)

                answer, context = result["answer"], result["context"]
                start_idx = context.find(answer)
                end_idx = start_idx + len(answer)
                # Hack due to this bug: https://github.com/streamlit/streamlit/issues/3190
                st.write(markdown(context[:start_idx] + str(annotation(answer, "ANSWER", "#8ef")) + context[end_idx:]), unsafe_allow_html=True)
                source = ""
                url = get_backlink(result)
                if url:
                    source = f"({result['document']['meta']['url']})"
                else:
                    source = f"{result['source']}"
                st.markdown(f"**Relevance:** {result['relevance']} -  **Source:** {source}")

            else:
                st.info("🤔 &nbsp;&nbsp; Haystack is unsure whether any of the documents contain an answer to your question. Try to reformulate it!")
                st.write("**Relevance:** ", result["relevance"])

            if eval_mode and result["answer"]:
                # Define columns for buttons
                is_correct_answer = None
                is_correct_document = None

                button_col1, button_col2, button_col3, _ = st.columns([1, 1, 1, 6])
                if button_col1.button("👍", key=f"{result['context']}{count}1", help="Correct answer"):
                    is_correct_answer=True
                    is_correct_document=True

                if button_col2.button("👎", key=f"{result['context']}{count}2", help="Wrong answer and wrong passage"):
                    is_correct_answer=False
                    is_correct_document=False

                if button_col3.button("👎👍", key=f"{result['context']}{count}3", help="Wrong answer, but correct passage"):
                    is_correct_answer=False
                    is_correct_document=True

                if is_correct_answer is not None and is_correct_document is not None:
                    try:
                        send_feedback(
                            query=question,
                            answer_obj=result["_raw"],
                            is_correct_answer=is_correct_answer,
                            is_correct_document=is_correct_document,
                            document=result["document"]
                        )
                        st.success("✨ &nbsp;&nbsp; Thanks for your feedback! &nbsp;&nbsp; ✨")
                    except Exception as e:
                        logging.exception(e)
                        st.error("🐞 &nbsp;&nbsp; An error occurred while submitting your feedback!")

            st.write("___")

        # if debug:
        #     st.subheader("REST API JSON response")
        #     st.write(st.session_state.raw_json)

main()
