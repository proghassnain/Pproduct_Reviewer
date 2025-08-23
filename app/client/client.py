from langchain_google_genai import ChatGoogleGenerativeAI

def llm_client():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.4,
    )
        
    return llm