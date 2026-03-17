import config
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

chat = ChatOpenAI(model = 'gpt-4', 
                  seed=365,
                  api_key=config.api_key,
                  temperature = 0)

response = chat.invoke('''I've recently adopted a dog. could you suggest some dog names?''')

response_parser = StrOutputParser()

response_txt = response_parser.invoke(response)
print(f"\n\n")
print(f"\nBot Response is:\n")
print(response_txt)
print(f"\n\n")
