import streamlit as st
import openai
from openai import OpenAIError
import os
import time
from datetime import datetime

st.set_page_config(layout="centered", initial_sidebar_state="collapsed")

st.title("🧑‍💼 모의 면접")

## 페이지 레이아웃
con1 = st.container(height=550, border=False)
con2, con3, con4 = st.columns(3)

# 사용자 정보와 API Key 확인 함수
user_info = st.session_state.get('user_info', None)
client = st.session_state.get('openai_client', None)

def check_user_info_and_api():
    with con1:
        if client is None:
            if st.button("사용자 정보에서 API Key가 입력되지 않았습니다."):
                st.switch_page("pages/1_User information.py")
            st.stop()

        if user_info is None or any(value is None for key, value in user_info.items() if key != '면접을 볼 회사') or set(user_info.keys()) == {"면접을 볼 회사"}:
                if st.button("사용자 정보가 입력되지 않았습니다."):
                    st.switch_page("pages/1_User information.py")
                st.stop()    

check_user_info_and_api()

## 면접 시작과 종료 여부 확인 함수
def get_interview_status():
    start_interview = st.session_state.get('interview_started', False)
    end_interview = st.session_state.get('interview_ended', False)

    return start_interview, end_interview

start_interview, end_interview = get_interview_status()

if "interview_messages" not in st.session_state:
        st.session_state.interview_messages = []

## 메시지 출력 함수
def show_message(msg):
    with con1:
        with st.chat_message(msg['role']):
            st.markdown(msg["content"])

for msg in st.session_state.interview_messages[2:]:
    show_message(msg)
    
## 서버에서 파일 받을 때 오류 발생시 재시도 함수
def get_file_content_infinite(client, output_file_id, wait_time=2):
    while True:
        try:
            new_data = client.files.content(output_file_id)
            return new_data
        except OpenAIError as e:
            print(e)
            time.sleep(wait_time)

## 면접 종료 함수
def end_interview_and_save():
    msg = {"role": "user", "content": "면접 종료"}
    st.session_state.interview_messages.append(msg)
    
    thread = st.session_state.thread

    assistant = st.session_state.assistant

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"""
                면접 내용을 요약해서 Q:질문 A:답변 형식으로 정리합니다. 
                이 때 첫 인사와 끝 인사는 맨 위와 아래에 각각 정리하세요.
                마지막 줄에는 면접이 종료되었습니다.를 작성하세요.
                정리된 내용은 '{user_info['면접을 볼 회사']} interview contents.txt'로 저장하세요.
                """
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    while run.status == 'requires_action':
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []

        for tool in tool_calls:
            func_name = tool.function.name
            kwargs = json.loads(tool.function.arguments)
            output = TOOL_FUNCTIONS.get(func_name, lambda **kwargs: None)(**kwargs)
            tool_outputs.append({"tool_call_id": tool.id, "output": str(output)})

        run = client.beta.threads.runs.submit_tool_outputs_and_poll(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )

    if run.status == 'completed':
        api_response = client.beta.threads.messages.list(
            thread_id=thread.id,
            run_id=run.id,
            order="asc"
        )
        
        output_file_id = api_response.data[0].content[0].text.annotations[0].file_path.file_id
        st.session_state.file_id = output_file_id
        new_data = get_file_content_infinite(client, output_file_id)
        current_time = datetime.now().strftime('%Y.%m.%d.%H.%M.%S')
        st.session_state.current_time = current_time
        filename = f"{current_time} {user_info['면접을 볼 회사']} interview contents.txt"

        os.makedirs("interview contents", exist_ok=True)

        with open(os.path.join("interview contents", filename), 'wb') as f:
            f.write(new_data.read())

        st.session_state["interview_started"] = False
        st.session_state["interview_ended"] = True
    else:
        st.error(f"Response not completed: {run.status}")

## 면접 시작 버튼
def start_interview_process():
    with con1:
        interview_company = st.text_input("면접을 볼 회사를 입력해주세요", 
                                        value=st.session_state.get('interview_company', ''))
        user_info["면접을 볼 회사"] = interview_company
        st.session_state.user_info = user_info

    with con4:
        if st.button("면접 시작", use_container_width=True):
            if not st.session_state.interview_messages:
                st.session_state.interview_messages = [{"role": "user", "content": f"""
                    당신은 모의면접관입니다. 사용자 정보에 따라 사용자에게 모의면접을 실시하세요

                    ## 사용자 정보
                    {user_info}
                """}]
            
            if "assistant" not in st.session_state:
                st.session_state.assistant = client.beta.assistants.create(
                    instructions="사용자 정보에 따라 모의 면접을 도와주세요.",
                    name="모의면접관",
                    model="gpt-4o-mini",
                    tools=[{"type": "code_interpreter"}]
                )
            
            elif "thread" not in st.session_state:
                st.session_state.thread = client.beta.threads.create(
                    messages=st.session_state.interview_messages
                )

            st.session_state["interview_started"] = True
            st.rerun()

## 면접 시행 중 문답
def interview_in_progress():
    if len(st.session_state.interview_messages) < 2:
        msg = {"role": "user", "content": "면접 시작"}
        st.session_state.interview_messages.append(msg)

        thread = st.session_state.thread

        assistant = st.session_state.assistant

        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content="면접 시작"
        )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        while run.status == 'requires_action':
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []

            for tool in tool_calls:
                func_name = tool.function.name
                kwargs = json.loads(tool.function.arguments)
                output = TOOL_FUNCTIONS.get(func_name, lambda **kwargs: None)(**kwargs)
                tool_outputs.append({"tool_call_id": tool.id, "output": str(output)})

            run = client.beta.threads.runs.submit_tool_outputs_and_poll(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )

        if run.status == 'completed':
            api_response = client.beta.threads.messages.list(
                thread_id=thread.id,
                run_id=run.id,
                order="asc"
            )
            
            for data in api_response.data:
                for content in data.content:
                    if content.type == 'text':
                        response = content.text.value
                        msg = {"role": "assistant", "content": response}
                        show_message(msg)
                        st.session_state.interview_messages.append(msg)
        else:
            st.error(f"Response not completed: {run.status}")

    if prompt := st.chat_input("질문에 대답하세요."):
        msg = {"role":"user", "content":prompt}
        show_message(msg)
        st.session_state.interview_messages.append(msg)

        thread = st.session_state.thread

        assistant = st.session_state.assistant

        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt
        )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        while run.status == 'requires_action':
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []

            for tool in tool_calls:
                func_name = tool.function.name
                kwargs = json.loads(tool.function.arguments)
                output = None

                if func_name in TOOL_FUNCTIONS:
                    output = TOOL_FUNCTIONS[func_name](**kwargs)

                tool_outputs.append(
                    {
                        "tool_call_id": tool.id,
                        "output": str(output)
                    }
                )

            run = client.beta.threads.runs.submit_tool_outputs_and_poll(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )

        if run.status == 'completed':
            api_response = client.beta.threads.messages.list(
                thread_id=thread.id,
                run_id=run.id,
                order="asc"
            )
            
            for data in api_response.data:
                for content in data.content:
                    if content.type == 'text':
                        response = content.text.value
                        msg = {"role":"assistant","content":response}
                        show_message(msg)
                        st.session_state.interview_messages.append(msg)
        else:
            st.error(f"Response not completed: {run.status}")

## 면접 끝내고 다운로드 버튼 표시
def end_interview_and_download():
    msg = {"role": "assistant", "content": "면접을 종료합니다."}
    show_message(msg)
    msg = {"role": "assistant", "content": "면접 내용을 다운받으시려면 다운로드 버튼을 눌러주세요. 다음 화면으로 넘어가고 싶으시다면 다음 버튼을 눌러주세요."}
    show_message(msg)

    with con2:
        with open(os.path.join("interview contents", f"{st.session_state.current_time} {user_info['면접을 볼 회사']} interview contents.txt"), "rb") as file:
            st.download_button(
                label="면접 내용 다운로드",
                data=file,
                file_name=f"{st.session_state.current_time} {user_info['면접을 볼 회사']} interview contents.txt",
                mime="text/csv",
                use_container_width=True
            )

    with con4:
        if st.button("다음", use_container_width=True):
            st.switch_page("pages/3_Interview result.py")
        st.stop()
st.write(user_info)
# 화면 흐름 제어
if start_interview:
    if "thread" not in st.session_state:
        st.rerun()
    interview_in_progress()
    with con4:
        if st.button("면접 종료", use_container_width=True):
            end_interview_and_save()
            st.rerun()

if not end_interview and not start_interview:
    start_interview_process()

if end_interview:
    end_interview_and_download()
