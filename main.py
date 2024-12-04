import streamlit as st

st.title("모의 면접 사이트")
st.subheader("유용합니다")

if st.button("모의 면접 시작하기"):
    st.switch_page("pages/1_User information.py")
st.stop()