import streamlit as st
import openai

# Streamlit 페이지 구성
st.title("AI 기반 면접 코칭 사이트")
st.write("OpenAI API를 활용해 원하는 직업에 맞는 면접 팁과 정보를 제공합니다.")

# OpenAI API Key 입력
api_key = st.text_input("OpenAI API 키를 입력하세요", type="password")

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
                response = openai.ChatCompletion.create(  # 최신 API 방식으로 수정
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "당신은 면접 코치입니다. 면접을 준비하는 데 필요한 상세한 자료와 팁을 제공합니다."},
                        {"role": "user", "content": f"{job_title} 직업에 대한 면접 준비 자료와 팁을 자세히 제공해주세요."},
                    ],
                    max_tokens=1000,  # 토큰 수를 늘려서 긴 응답을 받음
                    temperature=0.7,
                )
                # 응답을 여러 번에 걸쳐 출력
                tips = response['choices'][0]['message']['content']
                st.success("면접 준비 자료가 생성되었습니다!")
                st.write(f"### {job_title} 직업에 대한 면접 팁")
                
                # 출력 도중에 끊기지 않도록 실시간으로 데이터를 보여주기
                for tip in tips.split('\n'):
                    st.write(tip)  # 각 줄을 한 번에 출력
                
        except openai.OpenAIError as e:  # 최신 오류 처리 방식
            st.error(f"OpenAI API 오류가 발생했습니다: {str(e)}")
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")
