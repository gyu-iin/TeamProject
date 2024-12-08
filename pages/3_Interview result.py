import streamlit as st
import os

##면접 진행여부 확인
end_interview = st.session_state.get('interview ended', None)
if end_interview is None or not end_interview:
    if st.button("면접을 진행하지 않았습니다."):
        st.switch_page("pages/2_Mock Interview.py")
    st.stop()

##사용자 정보 업데이트
user_info = st.session_state.get('user_info', None)
if user_info is None:
    if st.button("사용자 정보가 입력되지 않았습니다."):
        st.switch_page("pages/1_User information.py")
    st.stop()

client = st.session_state.get('openai_client', None)
if client is None:
    if st.button("사용자 정보에서 API키가 입력되지 않았습니다."):
        st.switch_page("pages/1_User information.py")
    st.stop()

st.title("면접 결과 확인")

