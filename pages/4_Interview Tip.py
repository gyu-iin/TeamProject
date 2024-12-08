import streamlit as st
import openai

# Streamlit 페이지 구성
st.title("AI 기반 면접 코칭 사이트")
st.write("OpenAI API를 활용해 원하는 직업에 맞는 면접 팁과 정보를 제공합니다.")

# OpenAI API Key 입력
api_key = st.text_input("OpenAI API Key", 
                        value=st.session_state.get('api_key', ''), 
                        type='password')

# API Key 확인 후 세션 상태에 저장
if api_key:
    st.session_state['api_key'] = api_key
    if 'openai_client' not in st.session_state:
        openai.api_key = api_key  # API 키 설정
        st.session_state['openai_client'] = openai  # OpenAI 클라이언트 세션에 저장

# 원하는 직업 입력
job_title = st.text_input("원하는 직업을 입력하세요 (예: 데이터 분석가, 소프트웨어 엔지니어)")

# OpenAI API를 통해 면접 정보 생성
@st.cache_data
def get_interview_tips(job_title):
    # OpenAI API 호출
    if 'openai_client' in st.session_state:
        openai_client = st.session_state['openai_client']
        
        # `ChatCompletion.create` 방식으로 호출
        response = openai_client.ChatCompletion.create(  # `ChatCompletion.create` 사용
            model="gpt-3.5-turbo",  # 최신 모델 사용
            messages=[  # 메시지 형식으로 시스템 및 사용자 입력 설정
                {"role": "system", "content": "You are a professional interview coach. Please respond in Korean."},
                {"role": "user", "content": f"Provide detailed interview tips and preparation materials for the job of {job_title}."}
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return response['choices'][0]['message']['content'].strip()  # 응답에서 텍스트만 추출
    else:
        return "OpenAI 클라이언트가 초기화되지 않았습니다."

if st.button("면접 준비 자료 생성"):
    if not job_title:
        st.warning("직업명을 입력하세요.")
    elif not api_key:
        st.warning("OpenAI API 키를 입력하세요.")
    else:
        try:
            with st.spinner("AI가 면접 팁을 준비 중입니다..."):
                tips = get_interview_tips(job_title)

                # 글자가 초과하는 경우 마지막 문장까지 자르기 (숫자와 공백 포함)
                def truncate_text(text):
                    sentences = text.split('. ')
                    if len(sentences) > 1:
                        text_to_return = '. '.join(sentences[:-1]) + '.'
                        if text_to_return[-1].isdigit():
                            text_to_return = '. '.join(sentences[:-2]) + '.'
                        text_to_return = text_to_return.rstrip('0123456789. ')
                        return text_to_return
                    return text

                tips = truncate_text(tips).strip()

                st.success("면접 준비 자료가 생성되었습니다!")
                st.write(f"### {job_title} 직업에 대한 면접 팁")
                st.write(tips)

        except openai.OpenAIError as e:
            st.error(f"OpenAI API 오류가 발생했습니다: {str(e)}")
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")
