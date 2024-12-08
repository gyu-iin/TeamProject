import streamlit as st
import openai
import os

# Page title
st.title("면접 결과 확인")

## 면접 진행 여부 확인
end_interview = st.session_state.get('interview ended', None)
if end_interview is None or not end_interview:
    if st.button("면접을 진행하지 않았습니다."):
        st.switch_page("pages/2_Mock Interview.py")
    st.stop()

## 사용자 정보 확인
user_info = st.session_state.get('user_info', None)
if user_info is None:
    if st.button("사용자 정보가 입력되지 않았습니다."):
        st.switch_page("pages/1_User information.py")
    st.stop()

## OpenAI Client 확인
client = st.session_state.get('openai_client', None)
if client is None:
    if st.button("사용자 정보에서 API 키가 입력되지 않았습니다."):
        st.switch_page("pages/1_User information.py")
    st.stop()

# Chat history retrieval
if "result_messages" not in st.session_state:
    st.session_state.result_messages = []

# 면접 대화 기록 불러오기
interview_messages = st.session_state.get("interview_messages", [])

if not interview_messages:
    st.error("면접 대화 기록을 찾을 수 없습니다. 먼저 면접을 진행해주세요.")
    st.stop()

# Show previous messages (if any)
def show_message(msg):
    with st.chat_message(msg['role']):
        st.markdown(msg["content"])

for msg in st.session_state.result_messages[1:]:
    show_message(msg)

# 면접 결과 요약 및 점수 평가
if "interview_summary" not in st.session_state:
    st.session_state["interview_summary"] = None

if st.session_state["interview_summary"] is None:
    with st.spinner("면접 결과를 요약하고 점수를 평가 중입니다..."):
        try:
            # GPT 프롬프트 작성
            evaluation_prompt = f"""
            You are an expert interview evaluator. Summarize and score the following mock interview based on the content. Provide the following:
            1. A concise summary of the interview (bullet points are preferred).
            2. Feedback on the candidate's communication, relevance of answers, and adaptability.
            3. Provide individual scores out of 10 for:
              - Communication skills
              - Relevance to the questions asked
              - Adaptability
            4. A final overall score out of 10.
            
            ## Transcript:
            {interview_messages}
            """

            # `gpt-4o-mini` 모델로 요청
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # gpt 모델을 지정
                messages=[
                    {"role": "system", "content": "You are an expert mock interview evaluator."},
                    {"role": "user", "content": evaluation_prompt}
                ],
                temperature=0.7
            )

            summary = completion.choices[0].message.content
            st.session_state["interview_summary"] = summary

        except Exception as e:
            st.error(f"면접 결과 요약 또는 점수 평가 중 오류가 발생했습니다: {e}")
            st.stop()

# 결과 출력
summary = st.session_state.get("interview_summary", "")
if summary:
    st.markdown("### 면접 내용 요약")
    for section in summary.split("\n\n"):  # 섹션별 출력
        if section.strip():
            st.markdown(section.strip())

    st.markdown("### 평가 점수 및 피드백")
    feedback_start = summary.find("Feedback:")
    if feedback_start != -1:
        st.markdown(summary[feedback_start:])

# 다운로드 버튼
downloadable_text = f"""
Mock Interview Summary for {user_info['면접을 볼 회사']}:

{summary}
"""

st.markdown("### 다운로드 옵션")
st.download_button(
    label="결과 다운로드 (txt)",
    data=downloadable_text,
    file_name=f"{user_info['면접을 볼 회사']}_interview_summary.txt",
    mime="text/plain"
)

# 앱 다시 시작 옵션
if st.button("다시 시작하기"):
    st.session_state.clear()
    st.experimental_rerun()
