import config
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

chat = ChatOpenAI(model = 'gpt-4', 
                  seed=365,
                  api_key=config.api_key,
                  temperature = 0,
                  max_completion_tokens=100)

message_s = SystemMessage('''You are Marv, a chatbot that reluctantly answers questions with sarcastic responses.''')
message_h = HumanMessage('''I've recently adopted a dog. could you suggest some dog names?''')


response = chat.invoke([message_s, message_h])

print(f"\n\n")
print(f"\nBot Response is:\n")
print(response.content)