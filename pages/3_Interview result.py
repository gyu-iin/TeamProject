import streamlit as st
import openai
import os

# Page title
st.title("📖 면접 결과 확인 📖")

## 면접 진행 여부 확인
end_interview = st.session_state.get('interview_ended', None)
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

# 면접 대화 기록 불러오기 - 저장된 파일
with open(os.path.join("interview contents", f"{user_info["면접을 볼 회사"]} interview contents.txt"), "rb") as file:
    interview_messages = file

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
            {interview_messages}
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

        except Exception as e:
            st.error(f"면접 결과 요약 또는 점수 평가 중 오류가 발생했습니다: {e}")
            st.stop()

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
    file_name=f"{user_info['면접을 볼 회사']}_interview_summary.txt",
    mime="text/plain"
)

# 앱 다시 시작 옵션
if st.button("다시 시작하기"):
    del st.session_state.thread
    del st.session_state.interview_messages
    st.session_state.interview_ended = False
    st.switch_page("pages/1_User information.py")
st.stop()
