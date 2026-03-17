import config
from langchain_openai.chat_models import ChatOpenAI

chat = ChatOpenAI(model = 'gpt-4', 
                  seed=365,
                  api_key=config.api_key,
                  temperature = 0)

response = chat.invoke('''I've recently adopted a dog. could you suggest some dog names?''')

print(f"\n\n")
print(f"\nBot Response is:\n")
print(response.content)