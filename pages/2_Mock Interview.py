import streamlit as st
import openai
import os

col1, col2= st.columns(2)

with col1:
    st.title("모의 면접관")

#사용자 정보 업데이트
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

start_interview = st.session_state.get('interview started')
if start_interview is None:
    start_interview = False
else:
    if 'interview started' in st.session_state:
        start_interview = st.session_state['interview started']
    else:
        st.session_state['interview started'] = start_interview

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

def show_message(msg):
    with st.chat_message(msg['role']):
        st.markdown(msg["content"])

def save_uploaded_file(directory, file) :
    if not os.path.exists(directory) :
        os.makedirs(directory)

    with open(os.path.join(directory, file.name), 'wb') as f:
        f.write(file.getbuffer())

for msg in st.session_state.interview_messages[2:]:
    show_message(msg)
    
with col2:
    if start_interview:
        if st.button("면접 종료"):
            msg = {"role":"user", "content": "면접 내용 요약"}

            thread = st.session_state.thread

            assistant = st.session_state.assistant

            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=f"면접 내용을 요약해서 Q:질문 A:답변 형식으로 저장해서 '{user_info["면접을 볼 회사"]} interview result.txt'로 저장하세요. 그리고 파일 id를 반황하세요"
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
                st.write(run.status)
                api_response = client.beta.threads.messages.list(
                    thread_id=thread.id,
                    run_id=run.id,
                    order="asc"
                )
                st.write(print(api_response))
                # response = client.files.list()
                
                # output_file_id = response.data.id

                # file = client.files.retrieve_content(output_file_id)
                # if file is not None :
                #     save_uploaded_file('interview', file)
                
            else:
                st.error(f"Response not completed: {run.status}")

            st.session_state.interview_messages = []
            st.session_state["interview started"] = False
            st.session_state["interview ended"] = True

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

if end_interview:
    msg = {"role":"assistant","content":"면접을 종료합니다."}
    show_message(msg)
    msg = {"role":"assistant","content":"면접 내용을 다운받으시려면 다운로드 버튼을 눌러주세요. 바로 결과화면으로 넘어가고 싶으시다면 다음 버튼을 눌러주세요."}
    show_message(msg)
    col1, col2= st.columns(2)

    # with col1:
    #     st.download_button("면접 결과 다운로드", file_name = file)
    
    with col2:
        if st.button("다음"):
            st.switch_page("pages/3_Interview result.py")
        st.stop()