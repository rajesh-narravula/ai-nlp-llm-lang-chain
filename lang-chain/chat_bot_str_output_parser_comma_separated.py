import config
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import CommaSeparatedListOutputParser

chat = ChatOpenAI(model = 'gpt-5-nano', 
                  seed=365,
                  api_key=config.api_key,
                  temperature = 0)

message_h = HumanMessage(content=f'''I've recently adopted a dog. could you suggest some dog names?                         
                         {CommaSeparatedListOutputParser().get_format_instructions()}''')
response = chat.invoke([message_h])

response_parser = CommaSeparatedListOutputParser()

response_txt = response_parser.invoke(response)

print(f"\n\n")
print(f"\nBot Response is:\n")
print(response_txt)
print(f"\n\n")
