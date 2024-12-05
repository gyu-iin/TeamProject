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

user_name = st.text_input("이름을 입력해주세요", value =st.session_state.get('user_name',''))
user_age = st.text_input("나이를 입력해주세요", value =st.session_state.get('user_age',''))
user_field = st.text_input("면접을 보고자 하는 분야를 입력해주세요", value =st.session_state.get('user_field',''))
user_edu = st.text_input("학력 사항을 입력해주세요", value =st.session_state.get('user_edu',''))

