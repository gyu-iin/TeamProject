import streamlit as st
import openai
from openai import OpenAIError
import os
import time


col1, col2= st.columns(2)

with col1:
    st.title("모의 면접관")

##사용자 정보 업데이트
user_info = st.session_state.get('user_info', None)
if user_info is None:
    if st.button("사용자 정보가 입력되지 않았습니다."):
        st.switch_page("pages/1_User information.py")
    st.stop()

client = st.session_state.get('openai_client', None)
if client is None:
    if st.button("사용자 정보에서 API Key가 입력되지 않았습니다."):
        st.switch_page("pages/1_User information.py")
    st.stop()

##면접 시작 여부 확인
start_interview = st.session_state.get('interview started')
if start_interview is None:
    start_interview = False
else:
    if 'interview started' in st.session_state:
        start_interview = st.session_state['interview started']
    else:
        st.session_state['interview started'] = start_interview

##면접 종료 여부 확인
end_interview = st.session_state.get('interview ended')
if end_interview is None:
    end_interview = False
else:
    if 'interview ended' in st.session_state:
        end_interview = st.session_state['interview ended']
    else:
        st.session_state['interview ended'] = end_interview

if "interview_messages" not in st.session_state:
        st.session_state.interview_messages = []

##메시지 출력 함수
def show_message(msg):
    with st.chat_message(msg['role']):
        st.markdown(msg["content"])

##이전 메시지 출력
for msg in st.session_state.interview_messages[2:]:
    show_message(msg)

##서버에서 파일 받을때 오류 발생시 재시도하는 함수
def get_file_content_infinite(client, output_file_id, wait_time=2):
    while True:
        try:
            new_data = client.files.content(output_file_id)
            print("File content retrieved successfully.")
            return new_data
        except OpenAIError as e:
            print(f"Error occurred: {e}")
            print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

##면접 종료 버튼 - 면접 종료와 동시에 이때까지의 대화내용을 txt파일로 저장
with col2:
    if start_interview:
        if st.button("면접 종료"):
            msg = {"role":"user", "content": "면접 내용 요약"}

            thread = st.session_state.thread

            assistant = st.session_state.assistant

            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=f"면접 내용을 요약해서 Q:질문 A:답변 형식으로 저장해서 '{user_info["면접을 볼 회사"]} interview contents.txt'로 저장하세요."
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
                
                output_file_id = api_response.data[0].content[0].text.annotations[0].file_path.file_id
                new_data = get_file_content_infinite(client, output_file_id)
                filename = f"{user_info["면접을 볼 회사"]} interview contents.txt"

                if not os.path.exists("interview contents"):
                    os.makedirs("interview contents")

                with open(os.path.join("interview contents", filename),'wb') as f:
                    f.write(new_data.read())
                
            else:
                st.error(f"Response not completed: {run.status}")

            st.session_state["interview started"] = False
            st.session_state["interview ended"] = True

##면접을 볼 회사를 정한 후 면접을 시작하는 버튼
if not end_interview:
    if not start_interview:
        interview_company = st.text_input("면접을 볼 회사를 입력해주세요", 
                                value=st.session_state.get('interview_company',''))
        user_info["면접을 볼 회사"] = interview_company
        st.session_state.user_info = user_info

        if st.button("면접 시작"):
            if st.session_state.interview_messages == []:
                st.session_state.interview_messages = [
                    {"role":"user","content":f"""
            당신은 모의면접관입니다. 사용자 정보에 따라 사용자에게 모의면접을 실시하세요

            ## 사용자 정보
            {user_info}        
            """}
                ]   
            
            if "assistant" not in st.session_state:
                st.session_state.assistant = client.beta.assistants.create(
                    instructions="사용자 정보에 따라 모의 면접을 도와주세요.",
                    name="모의면접관",
                    model="gpt-4o-mini",
                    tools=[{"type":"code_interpreter"}]
                )

            if "thread" not in st.session_state:
                st.session_state.thread = client.beta.threads.create(
                    messages = st.session_state.interview_messages  
                )
            start_interview = True
            st.session_state["interview started"] = start_interview

##면접 시행중 문답을 진행하는 코드
if start_interview:
    if len(st.session_state.interview_messages) < 2:
        msg = {"role":"user", "content": "면접 시작"}
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

##면접을 끝낸 후 내용을 다운로드 하는 버튼과 다음 화면으로 넘어가는 버튼 표시
if end_interview:
    msg = {"role":"assistant","content":"면접을 종료합니다."}
    show_message(msg)
    msg = {"role":"assistant","content":"면접 내용을 다운받으시려면 다운로드 버튼을 눌러주세요. 다음 화면으로 넘어가고 싶으시다면 다음 버튼을 눌러주세요."}
    show_message(msg)
    col1, col2= st.columns(2)

    with col1:
        with open(f"{user_info["면접을 볼 회사"]} interview contents.txt", "rb") as file:
            btn = st.download_button(
                label="면접 내용 다운로드",
                data=file,
                file_name=f"{user_info["면접을 볼 회사"]} interview contents.txt",
                mime="text/csv",
            )
    
    with col2:
        if st.button("다음"):
            st.switch_page("pages/3_Interview result.py")
        st.stop()