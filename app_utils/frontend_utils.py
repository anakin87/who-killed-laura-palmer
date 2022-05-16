import streamlit as st


def set_state_if_absent(key, value):
    if key not in st.session_state:
        st.session_state[key] = value

# Small callback to reset the interface in case the text of the question changes
def reset_results(*args):
    st.session_state.answer = None
    st.session_state.results = None
    st.session_state.raw_json = None

SIDEBAR_STYLE = """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child{
        width: 350px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child{
        width: 350px;
        margin-left: -350px;
    }
    a {text-decoration: none;}
    .haystack-footer {text-align: center;}
    .haystack-footer h4 {
        margin: 0.1rem;
        padding:0;
    }
    footer {opacity: 0;}
    .haystack-footer img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 85%;
    }
    </style>
"""         

SPOTIFY_IFRAME = """
    <p align="center">
    <iframe style="border-radius:12px" 
    src="https://open.spotify.com/embed/playlist/38rrtWgflrw7grB37aMlsO?utm_source=generator" 
    width="85%" height="380" frameBorder="0" allowfullscreen="" 
    allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture">
    </iframe>
    </p>
"""

TWIN_PEAKS_IMG_SRC = "https://upload.wikimedia.org/wikipedia/it/3/39/Twin-peaks-1990.jpg"
LAURA_PALMER_IMG_SRC = "https://static.wikia.nocookie.net/twinpeaks/images/e/ef/Laura_Palmer%2C_the_Queen_Of_Hearts.jpg"

              