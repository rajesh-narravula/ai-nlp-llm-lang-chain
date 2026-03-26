
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import CommaSeparatedListOutputParser

from pathlib import Path
import sys
# Go one level UP
sys.path.append(str(Path(__file__).parent.parent))
import config

output_parser = CommaSeparatedListOutputParser().get_format_instructions()

messate_template = ChatPromptTemplate.from_messages([('human', '''I've recently adopted a {pet}. Could you suggest three {pet} names? \n '''+ output_parser)])

input_prompt = messate_template.invoke({'pet':'dog'})

print(input_prompt)

chat = ChatOpenAI(model='gpt-4o-mini',
                  seed=365,
                  temperature=0,
                  api_key=config.api_key,
                  max_completion_tokens=100)

response = chat.invoke(input_prompt)

list_oupput_parser = CommaSeparatedListOutputParser()

print(list_oupput_parser.invoke(response))
print("==================")
chain = messate_template | chat | list_oupput_parser
print(chain.invoke({'pet':'dog'}))