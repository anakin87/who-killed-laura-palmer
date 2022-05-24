# 📓 Notebooks
Jupyter/Colab notebooks to create the Search pipeline and generate questions, using [ 🔍 Haystack](https://github.com/deepset-ai/haystack).

## [Indexing and pipeline creation](./indexing_and_pipeline_creation.ipynb)

This notebook is inspired by ["Build Your First QA System" tutorial](https://haystack.deepset.ai/tutorials/first-qa-system), from Haystack documentation.

Here we use a collection of articles about Twin Peaks to answer a variety of questions about that awesome TV series!

The following steps are performed:
- load and preprocess data
- create (FAISS) document store and write documents
- initialize retriever and generate document embeddings
- initialize reader
- compose and try Question Answering pipeline
- save and export (FAISS) index

## [Question generation](./question_generation.ipynb)

This notebook is inspired by [Question Generation tutorial](https://haystack.deepset.ai/tutorials/question-generation), from Haystack documentation.

Here we use a collection of articles about Twin Peaks to generate a variety of questions about that awesome TV series!

The following steps are performed:

- load data
- create document store and write documents
- generate questions and save them


