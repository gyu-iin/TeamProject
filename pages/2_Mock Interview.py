import streamlit as st
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from lib.tools import Langchain_interview_question, SCHEMA_INTERVIEW

TOOL_FUNCTIONS = {
    "Langchain_interview_question": Langchain_interview_question
}

FUNCTION_TOOLS_SCHEMA = [
    SCHEMA_INTERVIEW
]

st.title("모의 면접관")

start_interview = st.session_state.get('interview started')
if start_interview is None:
    start_interview = False
else:
    if 'interview started' in st.session_state:
        start_interview = st.session_state['interview started']
    else:
        st.session_state['interview started'] = start_interview

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

def show_message(msg):
    with st.chat_message(msg['role']):
        st.markdown(msg["content"])

if "chatbot_messages" not in st.session_state:
    st.session_state.interview_messages = [
        {"role":"system","content":f"""
당신은 모의면접관입니다. 사용자 정보에 따라 사용자에게 모의면접을 실시하세요

## 사용자 정보
{user_info}        
"""}
    ]

for msg in st.session_state.interview_messages[2:]:
    show_message(msg)

if "interview_messages" not in st.session_state:
    st.session_state.interview_messages = []

if "assistant" not in st.session_state:
    st.session_state.assistant = client.beta.assistants.create(
        instructions="사용자 정보에 따라 모의 면접을 도와주세요.",
        name="모의면접관",
        model="gpt-4o-mini",
        tools = FUNCTION_TOOLS_SCHEMA
    )

if "thread" not in st.session_state:
    st.session_state.thread = client.beta.threads.create(
        messages = st.session_state.interview_messages
    )

col1, col2 = st.columns(2)

with col1:
    if st.button("Clear"):
        st.session_state.messages = []
        del st.session_state.thread

with col2:
    if st.button("Exit Chat"):
        st.session_state.messages = []
        del st.session_state.thread
        del st.session_state.assistant

if not start_interview:
    interview_company = st.text_input("면접을 볼 회사를 입력해주세요", 
                            value=st.session_state.get('interview_company',''))
    user_info["면접을 볼 회사"] = interview_company

    if st.button("면접 시작"):
        start_interview = True
        st.session_state["interview started"] = start_interview

if start_interview:
    if len(st.session_state.interview_messages) < 2:
        msg = {"role":"user", "content": "면접을 시작해줘"}

        thread = st.session_state.thread

        assistant = st.session_state.assistant

        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content="면접을 시작해줘"
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
    else:
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
