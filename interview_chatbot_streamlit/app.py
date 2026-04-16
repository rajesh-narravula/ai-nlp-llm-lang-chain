import time
from unicodedata import name
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="OpenAI API Example", page_icon="🤖")

st.title('Chatbot')

if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False
if "messages" not in st.session_state:
        st.session_state.messages = []
if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0
if "feedback_shown" not in st.session_state:
    st.session_state.feedback_shown = False
if "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False


def complete_setup():
    st.session_state.setup_complete = True

def show_feedback():
    st.session_state.feedback_shown = True

if not st.session_state.setup_complete:

    st.subheader("Personal Information", divider='rainbow')

    if "name" not in st.session_state:
        st.session_state.name = ""
    if "experiance" not in st.session_state:
        st.session_state.experiance = ""
    if "skills" not in st.session_state:
        st.session_state.skills = ""

    st.session_state["name"] = st.text_input("Name")
    st.session_state["experiance"] = st.text_area("Experiance")
    st.session_state["skills"] = st.text_area("Skills")

    st.write(f"**Your Name:** {st.session_state.name}")
    st.write(f"**Your Experience:** {st.session_state.experiance}")
    st.write(f"**Your Skills:** {st.session_state.skills}")

    st.subheader("Professional Summary", divider='rainbow')

    if "level" not in st.session_state:
        st.session_state.level = "Entry Level"
    if "industry" not in st.session_state:
        st.session_state.industry = "Software Development"
    if "company" not in st.session_state:
        st.session_state.company = "Apple"

    col1, col2 = st.columns(2)

    with col1:
        st.session_state["level"] = st.radio("Select your level", key= "visibility", options=["Entry Level", "Mid Level", "Senior Level"])
    with col2:
        st.session_state["industry"] = st.selectbox("Select your industry", ["Software Development", "Data Science", "Product Management", "Marketing", "Finance"])
        
    st.session_state["company"] = st.selectbox("Select your company", ['Apple', 'Microsoft', 'Google', 'Amazon', 'Meta', 'Tesla', 'Netflix', 'Nvidia', 'Samsung', 'Intel', 'IBM', 'Oracle', 'Adobe', 'Salesforce', 'Uber'])

    st.write(f" **Your information:** {st.session_state.level} in {st.session_state.industry} at {st.session_state.company}")

    if st.button("Complete Setup", on_click=complete_setup):
        st.success("Setup Complete! starting your interview..")
    

if st.session_state.setup_complete and not st.session_state.chat_complete and not st.session_state.feedback_shown:

    st.info( """
        Start by introducing yourself.
        """, 
        icon="👋"
    )

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4o-mini"

    if  not st.session_state.messages:
        st.session_state.messages = [{"role": "system", 
                                    "content": f"You are an HR executive that Interviews an interviewee called {st.session_state.name}"
                                    f"with {st.session_state.experiance} experience and {st.session_state.skills} skills. "
                                    f"You should interview them for the position of {st.session_state.level} in {st.session_state.industry}" 
                                    f"at company {st.session_state.company}."}]
   

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if st.session_state.user_message_count < 5:
        if prompt := st.chat_input("Your Answer is..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            if st.session_state.user_message_count < 4:
                with st.chat_message("assistant"):
                    stream = client.chat.completions.create(
                        model=st.session_state.openai_model,
                        messages=st.session_state.messages,
                        stream=True
                    )
                    response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})

        st.session_state.user_message_count += 1
    if st.session_state.user_message_count >= 5:
        st.session_state.chat_complete = True

if st.session_state.chat_complete and not st.session_state.feedback_shown:
    st.session_state.chat_complete = True
    if st.button("Provide Feedback", on_click=show_feedback):
        st.success("Thank you for participating in this interview!, Your feedback is....")

if st.session_state.feedback_shown:
    st.subheader("Feedback", divider='rainbow')

    conversation_summary = "\n".join([f"{message['role']}: {message['content']}" for message in st.session_state.messages])

    feedback_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    feedback_client_response = feedback_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """You are a helpful tool that provides feedback on an interviewee performance.
             Before the Feedback give a score of 1 to 10.
             Follow this format:
             Overal Score: //Your score
             Feedback: //Here you put your feedback
             Give only the feedback do not ask any additional questins.
              """},
            {"role": "user", "content": f"This is the interview you need to evaluate. Keep in mind that you are only a tool. And you shouldn't engage in any converstation: {conversation_summary}"}
        ]
    )

    st.write(feedback_client_response.choices[0].message.content)
