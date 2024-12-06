import streamlit as st

st.title("모의 면접관")

if start_interview in st.session_state:
    start_interview = st.session_state["interview started"]
else:
    start_interview = False

#사용자 정보 업데이트
user_info = st.session_state.get('user_info', None)
if user_info is None:
    if st.button("사용자 정보가 입력되지 않았습니다."):
        st.switch_page("pages/1_User information.py")
    st.stop()

client = st.session_state.get('openai_client', None)
if client is None:
    if st.button("사용자 정보에서 API Key가 입력되지 않았습니다."):
        st.switch_page("pages/1_User information.py")
    st.stop()

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

if "chatbot_messages" not in st.session_state:
    st.session_state.chatbot_messages = [
        {"role":"system","content":f"""
사용자 정보를 이용하여 모의면접을 실시하세요

## 사용자 정보
{user_info}        
"""}
    ]
    for msg in st.session_state.interview_messages:
        show_message(msg)

while not start_interview:
    interview_company = st.text_input("면접을 볼 회사를 입력해주세요", 
                            value=st.session_state.get('interview_company',''))
    user_info["면접을 볼 회사"] = interview_company

    if st.button("면접 시작"):
        start_interview = True
        st.session_state["interview started"] = start_interview

while start_interview:
    if prompt := st.chat_input("질문에 대답하세요."):
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
