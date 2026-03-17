from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
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

messate_template = ChatPromptTemplate.from_messages([('human', '''I've recently adopted a {pet} which is a {breed}. Could you suggest several training tips?''')])

chain = messate_template | chat

generator_response = chain.stream({'pet':'dragon', 'breed':'night fury'}) # batching and stream output.

for i in generator_response:    
    print(i.content, end='')