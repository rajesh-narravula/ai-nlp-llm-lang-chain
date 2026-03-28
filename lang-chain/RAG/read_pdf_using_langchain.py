from langchain_community.document_loaders import PyPDFLoader
import copy

pdf_file_loader = PyPDFLoader(r"RAG\Introduction_to_Data_and_Data_Science.pdf")

pdf_content = pdf_file_loader.load()

pdf_content_cut = copy.deepcopy(pdf_content)

for i in pdf_content_cut:
    i.page_content = ' '.join(i.page_content.split())

print(pdf_content_cut)
