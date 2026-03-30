import config
from langgraph.graph import START, END, StateGraph, MessagesState
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from typing import Literal
from pydantic import SecretStr

chat = ChatOpenAI(model="gpt-4o-mini",
                  temperature=0,
                  api_key=SecretStr(config.api_key),
                  max_completion_tokens=300)

def ask_question(_: MessagesState) -> MessagesState:
     print(f"\n-------> ENTERING Ask_question:")
     question = "What is the question:"
     print(question)
     return MessagesState(messages=[AIMessage(question), HumanMessage(input())])

def chatbot(state: MessagesState) -> MessagesState:
     print(f"\n-------> ENTERING chatbot:")
     response = chat.invoke(state["messages"])
     response.pretty_print()
     return MessagesState(messages=[response])

def ask_another_question(_: MessagesState) -> MessagesState:
     print(f"\n-------> ENTERING Ask_another_question:")
     question = "Do you have any other question(yes/no):"
     print(question)
     return MessagesState(messages=[AIMessage(question), HumanMessage(input())])

def routing_function(state: MessagesState) -> Literal["ask_question", "__end__"]:
     if state["messages"][-1].content == 'yes':
        return "ask_question"
     else:
        return "__end__"


graph_state = StateGraph(MessagesState)

graph_state.add_node("ask_question", ask_question)
graph_state.add_node("chatbot", chatbot)
graph_state.add_node("ask_another_question", ask_another_question)

graph_state.add_edge(START, "ask_question")
graph_state.add_edge("ask_question", "chatbot")
graph_state.add_edge("chatbot", "ask_another_question")
graph_state.add_conditional_edges(source="ask_another_question", path=routing_function)

graph_compiled = graph_state.compile()

#print(graph_compiled.get_graph().draw_ascii())

graph_compiled.invoke(MessagesState(messages = []))


