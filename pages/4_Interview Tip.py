import streamlit as st
import openai

st.set_page_config(layout="centered")

# Streamlit 페이지 구성
st.title("📌 AI가 제공하는 면접팁 📌")
st.write("OpenAI API를 활용해 원하는 직업에 맞는 면접 팁과 정보를 제공합니다.")

# OpenAI API Key 입력
api_key = st.text_input("OpenAI API Key", 
                        value=st.session_state.get('api_key',''),
                        type='password')

# 원하는 직업 입력
job_title = st.text_input("원하는 직업을 입력하세요 (예: 데이터 분석가, 소프트웨어 엔지니어)")

# API Key 확인
if not api_key:
    st.warning("OpenAI API 키를 입력하세요.")
else:
    openai.api_key = api_key

@st.cache_data
def get_interview_tips(job_title):
    # OpenAI API 호출
    return response['choices'][0]['message']['content']

# OpenAI API를 통해 면접 정보 생성
if st.button("면접 준비 자료 생성"):
    if not job_title:
        st.warning("직업명을 입력하세요.")
    else:
        try:
            with st.spinner("AI가 면접 팁을 준비 중입니다..."):
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a professional interview coach. Please respond in Korean."},
                        {"role": "user", "content": f"Provide detailed interview tips and preparation materials for the job of {job_title}."},
                    ],
                    max_tokens=500,
                    temperature=0.7,
                )
                tips = response['choices'][0]['message']['content']

                # 글자가 초과하는 경우 마지막 문장까지 자르기 (숫자와 공백 포함)
                def truncate_text(text):
                    # 숫자와 공백을 포함하여 마지막 문장 잘라내기
                    sentences = text.split('. ')
                    if len(sentences) > 1:
                        text_to_return = '. '.join(sentences[:-1]) + '.'  # 마지막 문장 제외
                        # 숫자와 공백을 포함하여 끝부분 잘리기
                        if text_to_return[-1].isdigit():
                            text_to_return = '. '.join(sentences[:-2]) + '.'
                        # 마지막 문장이 숫자일 경우 해당 부분 제거
                        text_to_return = text_to_return.rstrip('0123456789. ')  # 숫자와 공백 및 점 제거
                        return text_to_return
                    return text

                # 짤린 부분까지 제거
                tips = truncate_text(tips).strip()

                st.success("면접 준비 자료가 생성되었습니다!")
                st.write(f"### {job_title} 직업에 대한 면접 팁")
                st.write(tips)

        except openai.OpenAIError as e:
            st.error(f"OpenAI API 오류가 발생했습니다: {str(e)}")
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")
