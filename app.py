
import streamlit as st
import requests

st.title("RAG System Chatbot")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat historyA
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Enter your query:"):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Send query to Flask backend
    try:
        response = requests.post(
            "http://localhost:7000/query",
            json={"query": prompt, "history": st.session_state.messages}
        )
        if response.status_code == 200:
            answer = response.json().get("answer")
            with st.chat_message("assistant"):
                st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            st.error("Error: Could not get response from backend.")
    except requests.RequestException:
        st.error("Error: Backend not reachable.")
