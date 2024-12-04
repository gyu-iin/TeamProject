import streamlit as st
from openai import OpenAI

# client = st.session_state.get('openai_client', None)
# if client is None:
#     if st.button("사용자 정보에서 API Key가 입력되지 않았습니다."):
#         st.switch_page("pages/1_User information.py")
#     st.stop()
api_key = st.text_input("OpenAI API Key", 
                        value=st.session_state.get('api_key',''),
                        type='password')

if api_key:
    st.session_state['api_key'] = api_key
    if 'openai_client' in st.session_state:
        client = st.session_state['openai_client']
    else:
        client = OpenAI(api_key=api_key)
        st.session_state['openai_client'] = client

def show_message(msg):
    with st.chat_message(msg['role']):
        st.markdown(msg["content"])

if "interview_messages" not in st.session_state:
    st.session_state.interview_messages = []

if "assistant" not in st.session_state:
    st.session_state.assistant = client.beta.assistants.create(
        instructions="사용자 정보에 따라 모의 면접을 도와주세요.",
        name="모의면접관",
        model="gpt-4o-mini"
    )

if "thread" not in st.session_state:
    st.session_state.thread = client.beta.threads.create()

for msg in st.session_state.chatpdf_messages:
    show_message(msg)

if prompt := st.chat_input("Ask any question"):
    msg = {"role":"user", "content":prompt}
    show_message(msg)
    st.session_state.interview_messages.append(msg)

    thread = st.session_state.thread

    assistant = st.session_state.assistant

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    if run.status == 'completed':
        api_response = client.beta.threads.messages.list(
            thread_id=thread.id,
            run_id=run.id,
            order="asc"
        )
        for data in api_response.data:
            for content in data.content:
                if content.type == 'text':
                    response = content.text.value
                    msg = {"role":"assistant","content":response}
                    show_message(msg)
                    st.session_state.interview_messages.append(msg)
    else:
        st.error(f"Response not completed: {run.status}")