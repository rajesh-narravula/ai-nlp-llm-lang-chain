from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables import RunnableParallel
from langchain_core.output_parsers import StrOutputParser

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
import config

store_vectors = Chroma(persist_directory="./chroma_db", 
                       embedding_function=OpenAIEmbeddings(model="text-embedding-3-small", api_key=config.api_key))

retriver = store_vectors.as_retriever(search_type="mmr", 
                                      search_kwargs={"k": 3, "lambda_mult": 0.7})


TEMPLATE = '''
            Answer the following question:
            {question}

            To answer the question, use only the following context:
            {context}

            At the end of the response, specify the name of the lecture this context is taken from in the format:
            Resources: *Lecture Title*
            where *Lecture Title* should be substituted with the title of all resource lectures.

            '''

prompt = PromptTemplate.from_template(TEMPLATE)

chat = ChatOpenAI(model='gpt-4o-mini', api_key=config.api_key, temperature=0, max_completion_tokens=500)

chain = {"context": retriver, "question":RunnablePassthrough()} | prompt | chat | StrOutputParser()

question = "What software do data scientists use?"

print(chain.invoke(question))
