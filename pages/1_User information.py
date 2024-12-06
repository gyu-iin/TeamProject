import streamlit as st
from openai import OpenAI

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


if user_name or user_age or user_field or user_edu or user_exp:
    st.session_state['user_name'] = user_name
    st.session_state['user_age'] = user_age
    st.session_state['user_field'] = user_field
    st.session_state['user_edu'] = user_edu
    st.session_state['user_exp'] = user_exp
    if 'user_info' in st.session_state:
        user_info = st.session_state['user_info']
    else:
        user_info = {"이름": user_name, "나이" : user_age, "관심분야" : user_field, "학력" : user_edu, "경력사항" : user_exp, "면접을 볼 회사":""}
        st.session_state['user_info'] = user_info

col1, col2 = st.columns(2)

with col1:
    if st.button("사용자 정보 삭제"):
        st.write(user_info)
        for i in user_info.keys():
            user_info[i] = None
            st.session_state[i] = None
            
        st.session_state['user_info'] = user_info
        st.write(user_info)

with col2:
    if st.button("면접 시작"):
        st.switch_page("pages/2_Mock interview.py")
    st.stop()
