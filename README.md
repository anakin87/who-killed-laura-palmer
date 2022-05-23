---
title: Who killed Laura Palmer?
emoji: 🗻🗻
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.2.0
app_file: app.py
pinned: false
license: mit
---

# Who killed Laura Palmer? &nbsp; [![Generic badge](https://img.shields.io/badge/🤗-Open%20in%20Spaces-blue.svg)](https://huggingface.co/spaces/anakin87/who-killed-laura-palmer) [![Generic badge](https://img.shields.io/github/stars/anakin87/who-killed-laura-palmer?label=Github&style=social)](https://github.com/anakin87/who-killed-laura-palmer)
## 🗻🗻 Twin Peaks Question Answering system

WKLP is a simple Question Answering system, based on data crawled from [Twin Peaks Wiki](https://twinpeaks.fandom.com/wiki/Twin_Peaks_Wiki). It is built using [🔍 Haystack](https://github.com/deepset-ai/haystack), an awesome open-source framework for building search systems that work intelligently over large document collections.

---

## Project architecture 🧱

![Project architecture](./data/readme_images/project_architecture.png) 

* Crawler: implemented using [Scrapy](https://github.com/scrapy/scrapy) and [fandom-py](https://github.com/NikolajDanger/fandom-py)
* Question Answering pipelines: created with [Haystack](https://github.com/deepset-ai/haystack)
* Web app: developed with [Streamlit](https://github.com/streamlit/streamlit)
* Free hosting: [Hugging Face Spaces](https://huggingface.co/spaces)

---

## What can I learn from this project? 📚