import streamlit as st
from openai import OpenAI

st.title("🖊 면접을 시작하기 전에 당신의 정보를 입력해주세요! 🖊")

api_key = st.text_input("OpenAI API Key", 
                        value=st.session_state.get('api_key',''),
                        type='password')

if api_key:
    st.session_state['api_key'] = api_key
    if 'openai_client' in st.session_state:
        client = st.session_state['openai_client']
    else:
        client = OpenAI(api_key=api_key)
        st.session_state['openai_client'] = client

keys = ['user_name', 'user_age', 'user_field', 'user_edu', 'user_exp']

user_info = {
        "이름": None,
        "나이": None,
        "관심분야": None,
        "학력": None,
        "경력사항": None,
        "면접을 볼 회사": None
    }

user_name = st.text_input("이름을 입력해주세요", 
                        value=st.session_state.get('user_name',''))
user_age = st.text_input("나이를 입력해주세요", 
                        value=st.session_state.get('user_age',''))
user_field = st.text_input("면접을 보고자 하는 분야를 입력해주세요", 
                        value=st.session_state.get('user_field',''))
user_edu = st.text_input("학력 사항을 입력해주세요(OO대학 OO학과졸업, OO고등학교졸업, OO대학원 OO박사 등)", 
                        value=st.session_state.get('user_edu',''))
user_exp = st.text_area("관련 경력사항을 자유롭게 입력해주세요", 
                        value=st.session_state.get('user_exp',''))

if user_name:
    st.session_state['user_name'] = user_name
    if 'user_info["이름"]' in st.session_state:
        user_info["이름"] = st.session_state['user_name']
    else:
        user_info["이름"] = st.session_state['user_name']
        st.session_state.user_info["이름"] = user_info["이름"]
if user_age:
    st.session_state['user_age'] = user_age
    if 'user_info["나이"]' in st.session_state:
        user_info["나이"] = st.session_state['user_name']
    else:
        user_info["나이"] = st.session_state['user_age']
        st.session_state.user_info["나이"] = user_info["나이"]
if user_field:
    st.session_state['user_field'] = user_field
    if 'user_info["관심분야"]' in st.session_state:
        user_info["관심분야"] = st.session_state['user_name']
    else:
        user_info["관심분야"] = st.session_state['user_field']
        st.session_state.user_info["관심분야"] = user_info["관심분야"]
if user_edu:
    st.session_state['user_edu'] = user_edu
    if 'user_info["학력"]' in st.session_state:
        user_info["학력"] = st.session_state['user_name']
    else:
        user_info["학력"] = st.session_state['user_edu']
        st.session_state.user_info["학력"] = user_info["학력"]
if user_exp:
    st.session_state['user_exp'] = user_exp
    if 'user_info["경력사항"]' in st.session_state:
        user_info["경력사항"] = st.session_state['user_name']
    else:
        user_info["경력사항"] = st.session_state['user_exp']
        st.session_state.user_info["경력사항"] = user_info["경력사항"]

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("사용자 정보 삭제"):
        if all(st.session_state.get(key) in (None, '') for key in keys):
            st.warning("사용자 정보가 없습니다.")
        else:
            for key in keys:
                st.session_state.pop(key, None)
            st.session_state['user_info'] = {"이름": None, "나이": None, "관심분야": None, "학력": None, "경력사항": None, "면접을 볼 회사": None}
            st.success("사용자 정보 삭제 완료")


with col2:
    if st.button("면접 꿀팁 얻으러 가기"):
        st.switch_page("pages/4_Interview Tip.py")

with col3:
    if st.button("면접 시작"):
        st.switch_page("pages/2_Mock Interview.py")
