import streamlit as st

client = st.session_state.get('openai_client', None)
if client is None:
    if st.button("사용자 정보에서 API Key가 입력되지 않았습니다."):
        st.switch_page("pages/1_User information.py")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "assistant" not in st.session_state:
    st.session_state.assistant = client.beta.assistants.create(
        instructions="사용자 정보에 따라 모의 면접을 도와주세요.",
        name="Assistant",
        model="gpt-4o-mini",
    )

if "thread" not in st.session_state:
    st.session_state.thread = client.beta.threads.create()