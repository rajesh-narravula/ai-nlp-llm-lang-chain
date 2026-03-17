import config
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

chat = ChatOpenAI(model = 'gpt-4', 
                  seed=365,
                  api_key=config.api_key,
                  temperature = 0,
                  max_completion_tokens=100)

message_h_dog = HumanMessage('''I've recently adopted a dog. could you suggest some dog names?''')
message_ai_dog = AIMessage('''Oh, absolutely. Because nothing screams "I'm a responsible pet owner" 
like asking a chatbot to name your new furball. How about "Bark Twain" (if it's a literary hound)?''')

message_h_cat = HumanMessage('''I've recently adopted a cat. could you suggest some cat names?''')
message_ai_cat = AIMessage('''Oh, absolutely. Because nothing screams "I'm a unique and creative individual" 
like asking a chatbot to name your cat. How about "Furry McFurFace", "Sir Meowsalot", or "Catastrophe"?''')

message_h_fish = HumanMessage('''I've recently adopted a dog. could you suggest some dog names?''')


response = chat.invoke([message_h_dog, message_ai_dog, message_h_cat, message_ai_cat, message_h_fish])

print(f"\n\n")
print(f"\nBot Response is:\n")
print(response.content)
print(f"\n\n")