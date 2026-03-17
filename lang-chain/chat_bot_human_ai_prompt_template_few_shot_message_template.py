import config
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import AIMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, FewShotChatMessagePromptTemplate

chat = ChatOpenAI(model = 'gpt-4', 
                  seed=365,
                  api_key=config.api_key,
                  temperature = 0,
                  max_completion_tokens=100)


TEMPLATE_H = '''I've recently adopted a {pet}. Could you suggest some {pet} names?'''
TEMPLATE_AI = '{response}'

message_h = HumanMessagePromptTemplate.from_template(TEMPLATE_H)
message_s = AIMessagePromptTemplate.from_template(TEMPLATE_AI)

examples = [{'pet':'dog', 
             'response':'''Oh, absolutely. Because nothing screams "I'm a responsible pet owner" 
              like asking a chatbot to name your new furball. How about "Bark Twain" (if it's a literary hound)? '''}, 
            
            {'pet':'cat', 
             'response':'''Oh, absolutely. Because nothing screams "I'm a unique and creative individual" 
             like asking a chatbot to name your cat. How about "Furry McFurFace", "Sir Meowsalot", or "Catastrophe"? '''}, 
            
            {'pet':'fish', 
             'response':
             '''Oh, absolutely. Because nothing screams "I'm a fun and quirky pet owner" 
             like asking a chatbot to name your fish. How about "Fin Diesel", "Gill Gates", or "Bubbles"?'''}]


chat_template = ChatPromptTemplate.from_messages([message_s, message_h])

few_shot_prompt = FewShotChatMessagePromptTemplate(examples=examples,
                                                   example_prompt=chat_template, 
                                                   input_variables = ['pet'])

final_message_template = ChatPromptTemplate.from_messages([few_shot_prompt, message_h])


# print(final_message_template)

final_message = final_message_template.invoke({'pet':'''rabbit'''})

# print(final_message)

response = chat.invoke(final_message)
print(f"\n\n")
print(f"\nBot Response is:\n")
print(response.content)
print(f"\n\n")