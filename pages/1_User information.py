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
user_info = {"이름": None, "나이" : None, "관심분야" : None, "학력" : None, "경력사항" : None, "면접을 볼 회사" : None}

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
if user_age:
    st.session_state['user_age'] = user_age
if user_field:
    st.session_state['user_field'] = user_field
if user_edu:
    st.session_state['user_edu'] = user_edu
if user_exp:
    st.session_state['user_exp'] = user_exp

if 'user_info' in st.session_state:
    user_info = st.session_state['user_info']
elif 'user_info' not in session_state or any(value is None for key, value in user_info.items() if key != '면접을 볼 회사'):
    for key in keys:
        for dic_key in user_info.keys():
            user_info[dic_key] = key
    st.session_state['user_info'] = user_info
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("사용자 정보 삭제"):
        if not user_name and not user_age and not user_field and not user_edu and not user_exp:
            st.write("삭제할 사용자 정보가 없습니다")
        else:
            for key in keys:
                if key is None:
                    continue
                st.session_state.pop(key, None)
            for key in user_info.keys():
                if st.session_state.user_info[key] is None:
                    continue
                st.session_state.user_info[key] = None
            st.write("사용자 정보 삭제 완료")


with col2:
    if st.button("면접 꿀팁 얻으러 가기"):
        st.switch_page("pages/4_Interview Tip.py")

with col3:
    if st.button("면접 시작"):
        st.switch_page("pages/2_Mock Interview.py")
