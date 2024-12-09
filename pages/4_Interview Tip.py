import streamlit as st
import openai
from openai import OpenAIError
import os

# Streamlit 기본 설정
st.set_page_config(layout="centered", initial_sidebar_state="collapsed")

st.title("💼 면접 준비 팁 제공")

con1 = st.container(height = 550, border = False)
con2, con3, con4 = st.columns([3, 4, 3])

with con1:
    client = st.session_state.get('openai_client', None)
    if client is None:
        st.warning("사용자 정보에서 API키가 입력되지 않았습니다.")
        if st.button("API 키 입력하러 가기"):
            st.switch_page("pages/1_User information.py")
        st.stop()

    user_info = st.session_state.get('user_info', None)
    if user_info is None or any(value is None for key, value in user_info.items() if key != '면접을 볼 회사'):
        if user_info is None:
            st.warning("사용자 정보가 입력되지 않았습니다.")
        elif any(value is None for key, value in user_info.items() if key != '면접을 볼 회사'):
            st.warning("사용자 정보 중 일부가 입력되지 않았습니다.")
        if st.button("사용자 정보 입력하러 가기"):
            st.switch_page("pages/1_User information.py")
        st.stop()

current_time = st.session_state.get('current_time', None)

uploaded_file = None

tip_started = st.session_state.get('tip_started', False)
tip_ended = st.session_state.get('tip_ended', False)

if 'tip_messages' not in st.session_state:
    st.session_state.tip_messages = []

if not os.path.exists("interview contents"):
            os.makedirs("interview contents", exist_ok = True)

interview_content = st.session_state.get('interview_content', None)

# 면접 준비 팁 생성 함수
@st.cache_data
def generate_tips_with_interview(messages):
    thread = st.session_state.tip_thread

    assistant = st.session_state.tip_assistant
    client.beta.threads.messages.create(
            thread_id = thread.id,
            role = "user",
            content = messages
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id = thread.id,
        assistant_id = assistant.id
        )
    
    if run.status == 'completed':
        api_response = client.beta.threads.messages.list(
            thread_id = thread.id,
            run_id = run.id,
            order = "asc"
        )
        st.write(print(api_response))
    tip_generate(api_response)

def tip_generate(api_response):    
    try:
        for data in api_response.data:
                for content in data.content:
                    if content.type == 'text':
                        response = content.text.value

        # 문장이 중간에 끊기지 않도록 처리
        if not response.endswith(("다.", "요.", "습니다.", "습니까?", "에요.")):
            response = response.rsplit('.', 1)[0] + '.'
        
        # 마지막 항목이 완전하게 마무리된 형태로 만들기
        if response.endswith(('.', '요.', '습니다.', '에요.')):
            return response
        else:
            response = response.rstrip()
            if response:
                response += '.'
            return response
    except OpenAIError as e:
        return f"OpenAI API 오류 발생: {e}", print(api_response)
    st.session_state.tip_started = False
    st.session_state.tip_ended = True

def show_message(tips):
    with con1:
        with st.chat_message("assistant"):
            st.markdown(tips)

with con1:
    for msg in st.session_state.tip_messages:
        show_message(msg)

with con1:
    if not tip_started:
        # 면접 기록 확인
        st.write("### 면접 기록")
        if interview_content is None:
            interview_contents_recorded = os.listdir("interview contents")
            if len(interview_contents_recorded) > 1:
                if interview_contents_recorded:
                    with st.expander("파일 목록" ,expanded = True):
                        for idx, file in enumerate(interview_contents_recorded):
                            with st.container(height=100, border=False):
                                if st.button(f"{idx + 1} {file}", use_container_width=True):
                                    interview_content = open(os.path.join("interview contents", file))
                                    st.session_state.interview_content = interview_content
                                st.divider()
                else:
                    st.warning("면접 기록이 없습니다. 먼저 모의 면접을 진행해주세요. 또는 파일이 존재한다면 업로드 해주세요")
                    uploaded_file = st.file_uploader("면접 기록 파일을 올려주세요")

                    col1, col2 = st.columns([2 , 5.5, 2.5])

                    with col2:
                        if st.button("면접 진행하러 가기"):
                            st.switch_page("pages/2_Mock Interview.py")

            if uploaded_file is not None:
                    with open(uploaded_file, "rb") as file:
                        interview_content = file.read()
                        st.session_state.interview_content = interview_content

        if interview_content is not None:
            st.write(interview_content)

        # 직업명 입력과 팁 생성
        st.write("### 면접 준비 팁 생성")
        with st.expander("선호 직업 입력하기"):
            job_title = st.text_input("직업명을 입력하세요 (예: 데이터 분석가, 소프트웨어 엔지니어)")

        interview_content = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in st.session_state.get("interview_messages", [])]
        ) if "interview_messages" in st.session_state else None

        if st.button("면접 준비 팁 생성"):
            if "tip_assistant" not in st.session_state:
                    st.session_state.tip_assistant = client.beta.assistants.create(
                        instructions = "사용자 정보와 면접 기록, 선호 직업을 참고하여 면접의 팁을 주세요",
                        name = "면접 보좌관",
                        model = "gpt-4o-mini"
                    )
            if "tip_thread" not in st.session_state:
                    st.session_state.tip_thread = client.beta.threads.create(
                        messages = st.session_state.tip_messages
                )
                
            if interview_content:
                messages = f"""
                    사용자의 면접 기록과, 사용자 정보, 선호 직업명을 참고하여 면접 준비 팁을 작성해주세요.
                    면접 기록:
                    {interview_content}

                    사용자 정보:
                    {user_info}

                    선호 직업명:
                    {job_title}

                    작성 항목:
                    1. 면접 기록에 기반한 사용자 피드백
                    2. 선호 직업에 특화된 맞춤형 면접 준비 팁
                    각각의 항목을 명확히 구분하여 작성해주세요."""

            else:
                messages = f"""
                    사용자 정보와 선호 직업에 특화된 면접 준비 팁을 작성해주세요.
                    선호 직업:
                    {job_title}
                    
                    사용자 정보:
                    {user_info}

                    작성 항목:
                    1. 선호직업에 맞는 면접 준비 팁
                    """

            try: 
                with st.spinner("면접 준비 팁을 생성 중입니다..."):
                    tips = generate_tips_with_interview(messages)
                st.success(f'{job_title}에 대한 면접 준비 팁이 생성되었습니다!')
                tip_ended = True
            except Exception as e:
                    st.error(f"팁을 생성하는 도중 오류가 발생했습니다: {e}")
                    st.stop()
            msg = {"role": "assistant", "content": tips}
            show_message(msg)
            st.session_state.tip_messages.append(msg)

if tip_ended:
    with con2:
        if st.button("추가 면접 팁 생성"):
            
            messages = "추가 팁을 주세요"
            
            try:
                with st.spinner("추가 면접 준비 팁을 생성 중입니다..."):
                    tips = generate_tips_with_interview(messages)
                st.success(f'{job_title}에 대한 추가 면접 준비 팁이 생성되었습니다!')
                tip_ended = True
            except Exception as e:
                    st.error(f"추가 팁을 생성하는 도중 오류가 발생했습니다: {e}")
                    st.stop()
            msg = {"role": "assistant", "content": tips}
            show_message(msg)
            st.session_state.tip_messages.append(msg)

    with con4:
        st.subheader("꿀팁과 함께")
        if st.button("면접 진행하러 가기"):
            del st.session_state.thread
            del st.session_state.interview_messages
            st.session_state.interview_ended = False
            st.session_state.summary_started = False
            st.session_state.summary_ended = False
            st.session_state.tip_ended = False
            st.switch_page("pages/2_Mock Interview")