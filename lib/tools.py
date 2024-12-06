import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

@st.cache_data
def Langchain_interview_question(prompt):
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.9, api_key=st.session_state['api_key'])
    user_info = st.session_state['user_info']

    class interview_patton(BaseModel):
        company_name: str = Field(description=user_info["면접을 볼 회사"])
        question: str = Field(description="면접관의 질문")

    parser = JsonOutputParser(pydantic_object = interview_patton)

    prompt = PromptTemplate(
    template="당신은 면접관 입니다. 사용자의 답변에 의거하여 사용자와 면접을 실시합니다. \nFormat: {format_instructions}\n사용자의 답변: {prompt}\n",
    input_variables=["prompt"],
    partial_variables={"format_instructions": f"""면접 시작시에는 "{company_name}에 대한 면접을 시작합니다."로 시작하세요. 질문 시에는 사용자 정보와 대답에 따라 유동적인 질문을 하세요. 면접이 끝난 이후에는 "{company_name}에 대한 면접을 종료합니다."라는 말로 끝맺으세요"""}
    )

    chain = prompt | model | parser
    response = chain.invoke({"prompt": prompt})

    return response.text

SCHEMA_INTERVIEW = {
    "type":"function",
    "function": {
        "name": "Langchain_interview_question",
        "description":"generate interview question with langchain",
        "parameters": {
            "type":"object",
            "properties":{
                "prompt": {
                    "type":"string",
                    "description":"inviewee's information and company"
                }
            },
            "required":["prompt"],
            "additionalProperties": False
        },
        "strict": True
    }
}
