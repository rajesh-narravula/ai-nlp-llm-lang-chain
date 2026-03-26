from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
import config

chat_template_books = ChatPromptTemplate.from_template('''Suggest three of the best intermediate-level {programming language} books. 
    Answer only by listing the books.''')
chat_template_projects = ChatPromptTemplate.from_template('''Suggest three interesting {programming language} projects suitable for intermediate-level programmers. 
    Answer only by listing the projects.''')
chat = ChatOpenAI(model='gpt-4o-mini',
              seed=365,
              api_key=config.api_key,
              temperature=0,
              max_completion_tokens=500)

str_parser = StrOutputParser()

books_suggestions = chat_template_books | chat | str_parser
project_suggestions = chat_template_projects | chat | str_parser

parallel_suggestions = RunnableParallel({'books': books_suggestions, 'project': project_suggestions})

print(parallel_suggestions.invoke({'programming language': 'Python'}))

parallel_suggestions.get_graph().print_ascii()


