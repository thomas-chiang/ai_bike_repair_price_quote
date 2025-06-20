from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-001")
prompt = hub.pull("langchain-ai/chat-langchain-rephrase")

rephrasing_chain = prompt | llm | StrOutputParser()