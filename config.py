from langchain_ollama import ChatOllama

llm = ChatOllama(
    model = "gpt-oss:20b-cloud",
    temperature=0,
    format="json"
    
)