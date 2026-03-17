import config
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate

chat = ChatOpenAI(model = 'gpt-4', 
                  seed=365,
                  api_key=config.api_key,
                  temperature = 0,
                  max_completion_tokens=100)


TEMPLATE_S = '{description}'
TEMPLATE_H = '''I've recently adopted a {pet}. Could you suggest some {pet} names?'''

message_h = HumanMessagePromptTemplate.from_template(TEMPLATE_H)
message_s = SystemMessagePromptTemplate.from_template(TEMPLATE_S)

chat_template = ChatPromptTemplate.from_messages([message_s, message_h])

print(chat_template)

final_message = chat_template.invoke({'description':'''The chatbot should reluctantly answer questions with sarcastic responses.''',  'pet':'''dog'''})

print(final_message)

response = chat.invoke(final_message)
print(f"\n\n")
print(f"\nBot Response is:\n")
print(response.content)
print(f"\n\n")