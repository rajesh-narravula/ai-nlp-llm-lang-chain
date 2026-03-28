from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters.markdown import MarkdownHeaderTextSplitter
from langchain_text_splitters.character import CharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_chroma import Chroma
import hashlib


from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
import config

embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=config.api_key)

vector_store_from_directory = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

question = "What software do data scientists use?"

results_retriever = vector_store_from_directory.as_retriever(search_type="mmr",
                                                   search_kwargs={"k": 3, "lambda_mult": 0.7})


results = results_retriever.invoke(question)

print("\n\nResults for question: " + question + "\n")
for result in results:
    print('Content: ' + result.page_content)
    print('Lecture Title: ' + str(result.metadata['Lecture Title']))
    print("\n-----------------------\n")      




