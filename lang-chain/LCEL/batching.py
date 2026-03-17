from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pathlib import Path
import sys
# Go one level UP
sys.path.append(str(Path(__file__).parent.parent))
import config

chat = ChatOpenAI(model='gpt-4',
                  seed=365,
                  temperature=0,
                  api_key=config.api_key,
                  max_completion_tokens=100)

messate_template = ChatPromptTemplate.from_messages([('human', '''I've recently adopted a {pet}. Could you suggest three {pet} names?''')])

chain = messate_template | chat


single_prompt_response = chain.invoke({'pet':'dog'}) # single promt execution
batch_prompt_response = chain.batch([{'pet':'dog'},
                                     {'pet':'cat'}]) # batching the prompts.

print(single_prompt_response)
print("==================")
print(batch_prompt_response)