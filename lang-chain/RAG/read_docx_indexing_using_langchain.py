from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters.character import CharacterTextSplitter


doc_file_loader = Docx2txtLoader("RAG/Introduction_to_Data_and_Data_Science.docx")

doc_content = doc_file_loader.load()

for i in range(len(doc_content)):
    doc_content[i].page_content = ' '.join(doc_content[i].page_content.split())


text_splitter = CharacterTextSplitter(separator= "", 
                                      chunk_size = 500,
                                      chunk_overlap= 0)

doc_pager_split = text_splitter.split_documents(doc_content)

print(len(doc_pager_split))