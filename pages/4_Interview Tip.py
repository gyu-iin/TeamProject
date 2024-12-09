import streamlit as st
import openai
from openai import OpenAIError
import os

# Streamlit 기본 설정
st.set_page_config(layout="centered", initial_sidebar_state="collapsed")
st.title("💼 면접 준비 팁 제공")

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

# 면접 기록 확인
st.write("### 면접 기록")

interview_contents_recorded = os.listdir("interview_contents")
if len(interview_contents_recorded) > 1:
    if interview_contents_recorded:
        with st.expander("파일 목록" ,expanded = True):
            for idx, file in enumerate(interview_contents_recorded):
                with st.container(height=100, border=False):
                    if st.button(f"{idx + 1} {file}", use_container_width=True):
                        interview_content = open(os.path.join("interview contents", file))
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

if interview_contents is not None:
    st.write(interview_content)

# 면접 준비 팁 생성 함수
@st.cache_data
def generate_tips_with_interview():
    if interview_content:
        messages = [
            {"role": "system", "content": "당신은 면접 보좌관입니다."},
            {
                "role": "user",
                "content": f"""
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
                각각의 항목을 명확히 구분하여 작성해주세요."""}
        ]
    else:
        messages = [
            {"role": "system", "content": "당신은 면접 보좌관입니다."},
            {
                "role": "user",
                "content": f"""
                사용자 정보와 선호 직업에 특화된 면접 준비 팁을 작성해주세요.
                선호 직업:
                {job_title}
                
                작성 항목:
                1. 선호직업에 맞는 면접 준비 팁
                """
            }
        ]
    
    try:
        # client 객체를 통해 최신 방식으로 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        content = response.choices[0].message.content  # message에서 content 직접 접근

        # 문장이 중간에 끊기지 않도록 처리
        if not content.endswith(("다.", "요.", "습니다.", "습니까?", "에요.")):
            content = content.rsplit('.', 1)[0] + '.'
        
        # 마지막 항목이 완전하게 마무리된 형태로 만들기
        if content.endswith(('.', '요.', '습니다.', '에요.')):
            return content
        else:
            content = content.rstrip()
            if content:
                content += '.'
            return content
    except OpenAIError as e:
        return f"OpenAI API 오류 발생: {e}"

# 직업명 입력과 팁 생성
st.write("### 면접 준비 팁 생성")
with st.expander("선호 직업 입력하기"):
    job_title = st.text_input("직업명을 입력하세요 (예: 데이터 분석가, 소프트웨어 엔지니어)")

interview_content = "\n".join(
    [f"{msg['role']}: {msg['content']}" for msg in st.session_state.get("interview_messages", [])]
) if "interview_messages" in st.session_state else None

if st.button("면접 준비 팁 생성"):
    with st.spinner("면접 준비 팁을 생성 중입니다..."):
        tips = generate_tips_with_interview(job_title, interview_content)
    st.success(f'{job_title}에 대한 면접 준비 팁이 생성되었습니다!')
    with st.chat_message("assistant"):
            st.markdown(tips)
col1, col2 = st.columns([7, 3])

with col2:
    if st.button("면접 진행하러 가기"):
        st.switch_page("pages/2_Mock Interview")