import openai
import config

openai.api_key = config.api_key

client = openai.OpenAI(api_key=config.api_key)

completion = client.chat.completions.create(model = 'gpt-4',
                                            messages = [{'role':'system', 
                                                             'content':''' You are Marv, a chatbot that reluctantly    answers questions with sarcastic responses. '''},
                                                        {'role':'user', 
                                                            'content':''' I've recently adopted a dog. Could you suggest some dog names? '''}],
                                                    max_tokens=250)

print(completion.choices[0].message.content)