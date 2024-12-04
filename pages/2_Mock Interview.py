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

if "messages" not in st.session_state:
    st.session_state.messages = []

if "assistant" not in st.session_state:
    st.session_state.assistant = client.beta.assistants.create(
        instructions="사용자 정보에 따라 모의 면접을 도와주세요.",
        name="모의면접관",
        model="gpt-4o-mini"
    )

def show_message(msg):
    with st.chat_message(msg['role']):
        st.markdown(msg["content"])

if "thread" not in st.session_state:
    st.session_state.thread = client.beta.threads.create()

if prompt := st.chat_input("Ask any question"):
    msg = {"role":"user", "content":prompt}
    show_message(msg)
    st.session_state.messages.append(msg)

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

    for run_step in run_steps.data:
        if run_step.step_details.type == 'tool_calls':
            for tool_call in run_step.step_details.tool_calls:
                if tool_call.type == 'code_interpreter':
                    code = tool_call.code_interpreter.input
                    msg = {"role":"code","content":code}
                    show_message(msg)
                    st.session_state.messages.append(msg)