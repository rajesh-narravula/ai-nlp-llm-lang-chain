from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from pathlib import Path
import sys
# Go one level UP
sys.path.append(str(Path(__file__).parent.parent))
import config

chat = ChatOpenAI(model='gpt-4o-mini',
                  seed=365,
                  temperature=0,
                  api_key=config.api_key,
                  max_completion_tokens=100)

chat_template_tools = ChatPromptTemplate.from_template('''What are the five most important tools a {job title} needs? Answer only by listing the tools.''')

chat_template_strategy = ChatPromptTemplate.from_template('''Considering the tools provided, develop a strategy for effectively learning and mastering them: {tools} ''')


str_parser = StrOutputParser()

chain_tools = chat_template_tools | chat | str_parser | {'tools': RunnablePassthrough()}

chain_strategy = chat_template_strategy | chat | str_parser

chain = chain_tools | chain_strategy

print (chain.invoke({'job title': 'data scientist'}))

# other way is chain = chat_template_tools | chat | str_parser | {'tools': RunnablePassthrough()} | chat_template_strategy | chat | str_parser
# print (chain.invoke({'job title': 'data scientist'}))

chain.get_graph().print_ascii() # visualize the chain in graph format.

