import streamlit as st

st.set_page_config(page_title="모면, AI기반 모의면접",layout="wide", initial_sidebar_state="collapsed",page_icon="👔")

st.title("👔 모면 👔")
st.subheader("GPT-4o-Mini 모델을 활용한 AI 모의 면접 사이트")
st.subheader("자신감을 키우고 면접 실력을 한 단계 업그레이드하세요!")

col1, col2 = st.columns([2, 3])

with col1:
    st.image("img/main.jpg", caption="면접 준비의 시작!", use_container_width=True)

with col2:
    st.markdown("""
            ### ✨ 이 사이트에서 할 수 있는 것 ✨
            - AI 기반 모의 면접 진행 및 피드백
            - AI가 추천해주는 면접 팁

            **지금 바로 시작해보세요!**
    """)
    if st.button("모의 면접 시작하기"):
        st.switch_page("pages/1_User information.py")
