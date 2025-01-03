import streamlit as st
import openai
import os

# Page title
st.title("📖 면접 결과 확인 📖")

## OpenAI Client 확인
client = st.session_state.get('openai_client', None)
if client is None:
    st.warning("사용자 정보에서 API키가 입력되지 않았습니다.")
    if st.button("API 키 입력하러 가기"):
        st.switch_page("pages/1_User information.py")
    st.stop()

## 사용자 정보 확인
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

summary_started = st.session_state.get('summary_started', False)
summary_ended = st.session_state.get('summary_ended', False)

if not os.path.exists("interview contents"):
    os.makedirs("interview contents", exist_ok = True)

# Chat history retrieval
result_messages = st.session_state.get('result_messages', None)
if 'result messages' not in st.session_state:
    st.session_state.result_messages = []

# 면접 대화 기록 불러오기 - 저장된 파일
if result_messages is None:
    interview_contents_recorded = os.listdir("interview contents")
        if len(interview_contents_recorded) == 0:
            st.warning("면접 기록이 없습니다. 먼저 모의 면접을 진행해주세요. 또는 파일이 존재한다면 업로드 해주세요.")
            uploaded_file = st.file_uploader("면접 기록 파일을 올려주세요")
            col1, col2, col3 = st.columns([2 , 5.5, 2.5])

            with col3:
                if st.button("면접 진행하러 가기"):
                    st.switch_page("pages/2_Mock Interview.py")
            if uploaded_file is not None:
                interview_content = uploaded_file.getvalue()
                st.session_state.interview_content = interview_content

        elif len(interview_contents_recorded) > 0:
            with st.expander("파일을 선택해주세요", expanded=True):
                for idx, file in enumerate(interview_contents_recorded):
                    if st.button(f"{idx + 1} {file}", use_container_width=True):
                        with open(os.path.join("interview contents", file), "r", encoding="utf-8") as f:
                            interview_content = f.read()
                            st.session_state.interview_content = interview_content
                            st.write(interview_content)

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("면접 다시 진행하기"):
                    del st.session_state.thread
                    del st.session_state.interview_messages
                    st.session_state.interview_started = False
                    st.session_state.interview_ended = False
                    st.switch_page("pages/1_User information.py")

            with col3:
                if st.button("면접 페이지로 돌아가기"):
                    st.switch_page("pages/2_Interview.py")

    if uploaded_file is not None:
        with open(uploaded_file, "rb") as file:
            result_messages = file.read()
            st.session_state.result_messages = result_messages

# Show previous messages (if any)
def show_message(msg):
    with st.chat_message(msg['role']):
        st.markdown(msg["content"])

for msg in st.session_state.result_messages[1:]:
    show_message(msg)

# 면접 결과 요약 및 점수 평가
if "interview_summary" not in st.session_state:
    st.session_state["interview_summary"] = None

col1, col2 = st.columns([7, 3])

if not summary_started and not summary_ended:
    with col2:
        if st.button("면접 요약 확인하기"):
            summary_started = True
            st.session_state.summary_started = summary_started

if summary_started:
    with st.spinner("면접 결과를 요약하고 점수를 평가 중입니다..."):
        try:
            # GPT 프롬프트 작성
            evaluation_prompt = f"""
            당신은 전문가 인터뷰 평가자입니다. 면접 내용을 바탕으로 다음 모의 인터뷰를 요약하고 점수를 매기고 면접 결과를 한국어로 정리해야합니다.
            아래의 조건에 따라 당신은 면접에 점수를 매기고 종합적으로 피드백해야합니다.
            <평가 조건>
            1. 인터뷰 요약(벌렛 포인트 선호).
            2. 후보자의 커뮤니케이션, 답변의 적절성 및 적응력에 대한 피드백.
            3. 100점 만점에 개별 점수를 제공합니다:
            - 커뮤니케이션 기술(꼬리질문을 하였을때, 답변이 크게 흐트러지지 않거나 재치 있게 대답하는지 판단해야함.)
            - 질문과의 관련성(특히, 질문의 의도와 답변이 일치하는지 면밀하고 꼼꼼히 따져봐야함.)
            - 적응성(질문자의 출신, 학력, 경력, 스펙 등 다양한 요인을 비교하여 우리 회사의 분야와 적절한지, 입사 후 구성원과 잘 어울릴 수 있을지 판단해야함.)
            4. 최종 종합 점수 100점 만점.(단, 100점 만점을 매기면 안되고 답변이 매우 모범적인 답안이고 질문자의 의도를 잘 파악했다고 판단될때만 만점에 가깝게 점수를 부여할 수 있음.)
            
            ## Transcript:
            {result_messages}
            """

            # `gpt-4o-mini` 모델로 요청
            completion = client.chat.completions.create(
                model="gpt-4o-mini",  # gpt 모델을 지정
                messages=[
                    {"role": "system", "content": "You are an expert mock interview evaluator."},
                    {"role": "user", "content": evaluation_prompt}
                ],
                temperature=0.7
            )

            summary = completion.choices[0].message.content
            st.session_state["interview_summary"] = summary
            st.session_state.summary_started = False
            st.session_state.summary_ended = True

        except Exception as e:
            st.error(f"면접 결과 요약 또는 점수 평가 중 오류가 발생했습니다.")
            st.stop()

if summary_ended:
    # 결과 출력
    summary = st.session_state.get("interview_summary", "")
    if summary:
        st.markdown("📄 면접 내용 요약 📄")
        for section in summary.split("\n\n"):  # 섹션별 출력
            if section.strip():
                st.markdown(section.strip())

        st.markdown("🔬 평가 점수 및 피드백 🔬")
        feedback_start = summary.find("Feedback:")
        if feedback_start != -1:
            st.markdown(summary[feedback_start:])

    # 다운로드 버튼
    downloadable_text = f"""
    {user_info['면접을 볼 회사']}에서의 모의면접:

    {summary}
    """

    st.markdown("### 다운로드 옵션")
    st.download_button(
        label="결과 다운로드 (txt)",
        data=downloadable_text,
        file_name=f"{current_time} {user_info['면접을 볼 회사']}_interview_summary.txt",
        mime="text/plain"
    )
    col1, col2, col3 = st.columns([5, 1, 4])
    with col1:
        st.subheader("이번 면접이 어려웠다면")
        if st.button("면접 꿀팁 얻으러 가기"):
            st.switch_page("pages/4_Interview Tip.py")

    # 앱 다시 시작 옵션
    with col3:
        st.subheader("더 나은 면접을 위해")
        col3, col4 = st.columns([3.5, 6.5])
        with col4:
            if st.button("다시 시작하기"):
                if 'thread' in st.session_state:
                    del st.session_state.thread
                if 'interview_messages' in st.session_state:
                    del st.session_state.interview_messages
                del st.session_state.result_messages
                st.session_state.interview_ended = False
                st.session_state.summary_started = False
                st.session_state.summary_ended = False
                st.switch_page("pages/1_User information.py")
