from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from google.api_core.exceptions import ResourceExhausted, GoogleAPICallError

def invoke_llm_with_fallback(prompt_template, input_dict):
    """
    Tenta invocar a cadeia com o Google Gemini. Se falhar, tenta o Groq.
    """
    # TENTATIVA 1 GOOGLE GEMINI 
    try:
        print("Tentando LLM primário (Google Gemini)...")
        llm_gemini = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7, max_retries=0)
        chain = prompt_template | llm_gemini
        response = chain.invoke(input_dict)
        print("Sucesso com Gemini.")
        return response.content
    except (ResourceExhausted, GoogleAPICallError) as e:
        print(f"AVISO: API do Google Gemini falhou. Acionando fallback 1. Erro: {e}")

    # TENTATIVA 2: GROQ
    try:
        print("Tentando LLM de fallback (Groq com Llama 3.1)")
    
        llm_groq = ChatGroq(model_name="llama-3.1-8b-instant", temperature=0.7)
        chain = prompt_template | llm_groq
        response = chain.invoke(input_dict)
        print("Sucesso com Groq.")
        return response.content
    except Exception as e_groq:
        print(f"AVISO: API do Groq falhou. Acionando fallback final. Erro: {e_groq}")
    
