import streamlit as st

st.set_page_config(layout="wide")

st.title("모면")
st.subheader("GPT-4O-Mini 모델을 활용한 AI 모의 면접 사이트")
st.subheader("자신감을 키우고 면접 실력을 한 단계 업그레이드하세요!")

col1, col2 = st.columns([2, 3])

with col1:
    st.image("img/main.jpg", caption="면접 준비의 시작!", use_column_width=True)

with col2:
    st.markdown("""
    ### 이 사이트에서 할 수 있는 것:
    - AI 기반 모의 면접 피드백 제공
    - 다양한 산업별 질문 세트
    - 실시간 면접 시뮬레이션
    - 면접 영상 업로드 후 분석
    
    **지금 바로 시작해보세요!**
    """)

if st.button("서비스 이용하기"):
    st.switch_page("pages/1_User information.py")
    st.write("서비스 페이지로 이동 중...")
st.stop()
