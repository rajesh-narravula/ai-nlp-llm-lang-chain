from langgraph.graph import START, END, StateGraph, MessagesState
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, RemoveMessage
from langgraph.checkpoint.memory import InMemorySaver
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from pydantic import SecretStr

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
import config

class State(MessagesState):
    summary: str

chat = ChatOpenAI(model="gpt-4o-mini",
                  seed=365,
                  temperature=0,
                  api_key=SecretStr(config.api_key),
                  max_completion_tokens=300)

def ask_question(_: State) -> dict:
    print(f"\n-------> ENTERING ask_question:")
    print("What is your question:")
    return {"messages": [HumanMessage(input())]}

def chatbot(state: State) -> dict:
    print(f"\n-------> ENTERING chatbot:")

    system_message = f"""
    Here's a quick summary of what's been discussed so far:
    {state.get("summary", "")}

    Keep this in mind as you answer the next question.
    """

    response = chat.invoke([SystemMessage(system_message)] + state["messages"])
    response.pretty_print()
    return {"messages": [response]}

def summarize_messages(state: State) -> dict:
    print(f"\n-------> ENTERING summarize_messages:")

    new_conversation = ""
    for i in state["messages"]:
        new_conversation += f"{i.type}: {i.content}\n\n"

    summary_instructions = f'''
          Update the ongoing summary by incorporating the new lines of conversation below.
          Build upon the previous summary rather than repeating it,
          so that the result reflects the most recent context and developments.
          Respond only with the summary.

          Previous Summary:
          {state.get("summary", "")}

          New Conversation:
          {new_conversation}
          '''
    summary = chat.invoke([HumanMessage(summary_instructions)])

    remove_messages = [RemoveMessage(id=i.id) for i in state["messages"][:]]
    return {"messages": remove_messages, "summary": summary.content}

# ── Graph ──────────────────────────────────────────────────────────────────────
graph = StateGraph(State)

graph.add_node("ask_question", ask_question)
graph.add_node("chatbot", chatbot)
graph.add_node("summarize_messages", summarize_messages)

graph.add_edge(START, "ask_question")
graph.add_edge("ask_question", "chatbot")
graph.add_edge("chatbot", "summarize_messages")
graph.add_edge("summarize_messages", END)


db_path = "./langgraph.db"
con = sqlite3.connect(database = db_path, check_same_thread = False)

checkpointer = SqliteSaver(con)

checkpointer = SqliteSaver(con)
graph_compiled = graph.compile(checkpointer)

config1 = {"configurable": {"thread_id": "1"}}

graph_compiled.invoke(State(), config1)

