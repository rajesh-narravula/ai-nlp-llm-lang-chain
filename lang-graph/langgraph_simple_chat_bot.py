import config
from langgraph.graph import START, END, StateGraph
from typing_extensions import TypedDict
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, BaseMessage
from collections.abc import Sequence
from typing import Literal
from pydantic import SecretStr


class State(TypedDict):
    message: Sequence[BaseMessage]

chat = ChatOpenAI(model="gpt-4o-mini",
                  temperature=0,
                  api_key=SecretStr(config.api_key),
                  max_completion_tokens=300)

def ask_question(state: State) -> State:
     print(f"\n-------> ENTERING Ask_question:")
     print("What is the question:")
     return State(message=[HumanMessage(input())])

def chatbot(state: State) -> State:
     print(f"\n-------> ENTERING chatbot:")
     response = chat.invoke(state["message"])
     response.pretty_print()
     return State(message=[response])

def ask_another_question(state: State) -> State:
     print(f"\n-------> ENTERING Ask_another_question:")
     print("Do you have any other question(yes/no):")
     return State(message=[HumanMessage(input())])

def routing_function(state: State) -> Literal["ask_question", "__end__"]:
     if state["message"][0].content == 'yes':
        return "ask_question"
     else:
        return "__end__"


graph_state = StateGraph(State)

graph_state.add_node("ask_question", ask_question)
graph_state.add_node("chatbot", chatbot)
graph_state.add_node("ask_another_question", ask_another_question)

graph_state.add_edge(START, "ask_question")
graph_state.add_edge("ask_question", "chatbot")
graph_state.add_edge("chatbot", "ask_another_question")
graph_state.add_conditional_edges(source="ask_another_question", path=routing_function)

graph_compiled = graph_state.compile()

#print(graph_compiled.get_graph().draw_ascii())

graph_compiled.invoke(State(message = []))


