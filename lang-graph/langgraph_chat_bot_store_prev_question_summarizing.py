import config
from langgraph.graph import START, END, StateGraph,  MessagesState
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, RemoveMessage
from typing import Literal
from pydantic import SecretStr

class State(MessagesState):
    summary: str


chat = ChatOpenAI(model="gpt-4o-mini",
                  temperature=0,
                  api_key=SecretStr(config.api_key),
                  max_completion_tokens=300)

def ask_question( _: State) -> State:
     print(f"\n-------> ENTERING Ask_question:")
     question = "What is the question:"
     print(question)
     return State(messages=[AIMessage(question), HumanMessage(input())])

def chatbot(state: State) -> State:
     print(f"\n-------> ENTERING chatbot:")
     system_message = f'''
          Here's a quick summary of what's been discussed so far:
          {state.get("summary", "")}
    
          Keep this in mind as you answer the next question.
          '''
     response = chat.invoke([SystemMessage(system_message)] + state["messages"])
     response.pretty_print()
    
     return State(messages = [response])

def ask_another_question(_: State) -> State:
     print(f"\n-------> ENTERING Ask_another_question:")
     question = "Do you have any other question(yes/no):"
     print(question)
     return State(messages=[AIMessage(question), HumanMessage(input())])

def summarize_and_delete_messages(state: State) -> State:
    print(f"\n-------> ENTERING trim_messages:")
    
    new_conversation = ""
    for i in state["messages"]:
        new_conversation += f"{i.type}: {i.content}\n\n"
        
    summary_instructions = f'''
     Update the ongoing summary by incorporating the new lines of conversation below.  
     Build upon the previous summary rather than repeating it so that the result  
     reflects the most recent context and developments.


     Previous Summary:
     {state.get("summary", "")}

     New Conversation:
     {new_conversation}
     '''
    print(summary_instructions)
    
    summary = chat.invoke([HumanMessage(summary_instructions)])
    
    remove_messages = [RemoveMessage(id = i.id) for i in state["messages"][:]]
    
    return State(messages = remove_messages, summary = summary.content)


def routing_function(state: State) -> Literal["summarize_and_delete_messages", "__end__"]:
     if state["messages"][-1].content == 'yes':
        return "summarize_and_delete_messages"
     else:
        return "__end__"


graph_state = StateGraph(State)

graph_state.add_node("ask_question", ask_question)
graph_state.add_node("chatbot", chatbot)
graph_state.add_node("ask_another_question", ask_another_question)
graph_state.add_node("summarize_and_delete_messages", summarize_and_delete_messages)

graph_state.add_edge(START, "ask_question")
graph_state.add_edge("ask_question", "chatbot")
graph_state.add_edge("chatbot", "ask_another_question")
graph_state.add_conditional_edges(source="ask_another_question", path=routing_function)
graph_state.add_edge("summarize_and_delete_messages", "ask_question")

graph_compiled = graph_state.compile()

#print(graph_compiled.get_graph().draw_ascii())

graph_compiled.invoke(State(messages = []))


