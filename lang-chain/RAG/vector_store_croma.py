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

doc_file_loader = Docx2txtLoader("RAG/Introduction_to_Data_and_Data_Science_copy.docx")
doc_content = doc_file_loader.load()


md_text_splitter = MarkdownHeaderTextSplitter( headers_to_split_on = [("#", "Course Title"), ("##", "Lecture Title")])


page_md_split = md_text_splitter.split_text(doc_content[0].page_content)

for i in range(len(page_md_split)):
    page_md_split[i].page_content = ' '.join(page_md_split[i].page_content.split())

page_character_splitter = CharacterTextSplitter( separator= ".", chunk_size=500, chunk_overlap= 50)

page_character_split = page_character_splitter.split_documents(page_md_split)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=config.api_key)

vector_store = Chroma.from_documents(documents=page_character_split, 
                                     embedding = embeddings, 
                                     persist_directory="./chroma_db")


vector_store_from_directory = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# Create a unique ID based on the content
def generate_id(doc):    
    return hashlib.md5(doc.page_content.encode()).hexdigest()

ids = [generate_id(doc) for doc in page_character_split]

vector_store_from_directory.add_documents(page_character_split, ids=ids)

vector_store_from_directory.add_documents(page_character_split)

all_ids = vector_store_from_directory.get()['ids']
print(all_ids)




