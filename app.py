import streamlit as st
import os
import re
from PIL import Image
from src.agents.orchestrator.agent import app as report_agent_app
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

#  CSS 
st.markdown("""
<style>
/* Remove o fundo branco dos logos PNG */
[data-testid="stSidebar"] img {
    background-color: transparent;
}
[data-testid="stImage"] img {
    background-color: transparent;
}
/* Estilo customizado para o botão primário (azul profissional) */
.stButton button {
    background-color: #1c83e1;
    color: white;
    border-radius: 5px;
    border: none;
    padding: 10px 20px;
}
.stButton button:hover {
    background-color: #0b5fa5;
    color: white;
}
</style>
""", unsafe_allow_html=True)


def answer_follow_up_question(question: str, report_context: str) -> str:
    """Usa um LLM para responder a uma pergunta com base no relatório já gerado."""
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um assistente de IA..."),
        ("human", "Relatório:\n{context}\n\nPergunta:\n{question}")
    ])
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"context": report_context, "question": question})

st.set_page_config(
    page_title="Indicium HealthCare | Agente de Análise de SRAG",
    page_icon="src/images/indicium.png",  
    layout="wide"
)

with st.sidebar:
    try:
        logo_indicium = Image.open("src/images/indicium.png")
        st.image(logo_indicium)
    except FileNotFoundError:
        st.error("Logo da Indicium não encontrado.")

    st.header("Opções")
    if st.button("Iniciar Nova Análise", use_container_width=True):
        keys_to_clear = ["messages", "last_report"]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.divider()
    st.header("Sobre o Projeto")
    st.info(
        "Este projeto demonstra o uso de uma arquitetura de múltiplos agentes "
        "com LangGraph para automatizar a geração de relatórios complexos."
    )

col1, col2 = st.columns([1, 6])
with col1:
    try:
        logo_sus = Image.open("src/images/SUS.png")
        st.image(logo_sus, width=100)
    except FileNotFoundError:
        st.warning("Logo do SUS não encontrado.")

with col2:
    st.title("Agente Conversacional de Análise de SRAG")
    st.markdown("**Fonte de Dados:** OpenDataSUS")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Sou seu assistente de dados. Peça um relatório para uma localidade (ex: 'São Paulo', 'BR' ou 'Florianópolis, SC') para começar."}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "plots" in message and message["plots"]:
            st.subheader("Gráficos de Evolução")
            plot_col1, plot_col2 = st.columns(2)
            if "daily" in message["plots"]:
                with plot_col1:
                    st.image(message["plots"]["daily"], caption="Evolução Diária de Casos")
            if "monthly" in message["plots"]:
                with plot_col2:
                    st.image(message["plots"]["monthly"], caption="Evolução Mensal de Casos")
        if "pdf" in message and message["pdf"]:
            with open(message["pdf"], "rb") as pdf_file:
                st.download_button(
                    label="Baixar Relatório em PDF",
                    data=pdf_file,
                    file_name=os.path.basename(message["pdf"]),
                    mime="application/octet-stream"
                )

if "last_report" in st.session_state:
    if prompt := st.chat_input("Faça uma pergunta sobre o relatório acima..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Analisando o relatório para responder sua pergunta..."):
                response = answer_follow_up_question(prompt, st.session_state.last_report)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
else:
    if prompt := st.chat_input("Peça um relatório para uma localidade..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner(f"Entendido. Iniciando a análise completa para '{prompt}'..."):
                try:
                    city, state = None, prompt.strip()
                    match = re.match(r'^(.*?)[,\s-]+([A-Za-z]{2})$', prompt.strip())
                    if match:
                        city, state = match.group(1).strip(), match.group(2).strip().upper()
                    
                    initial_input = {"topic": state, "city": city}
                    final_state = report_agent_app.invoke(initial_input)
                    report_text = final_state.get("report_text", "Não foi possível gerar o relatório.")
                    plot_paths = final_state.get("plot_image_paths", {})
                    pdf_path = final_state.get("pdf_report_path")
                    st.markdown(report_text)
                    st.session_state.last_report = report_text
                    assistant_plots = {}
                    if "daily_cases_plot" in plot_paths:
                        assistant_plots["daily"] = plot_paths["daily_cases_plot"]
                    if "monthly_cases_plot" in plot_paths:
                        assistant_plots["monthly"] = plot_paths["monthly_cases_plot"]

                    assistant_message = {"role": "assistant", "content": report_text, "plots": assistant_plots}
                    if pdf_path and os.path.exists(pdf_path):
                        assistant_message["pdf"] = pdf_path
                    st.session_state.messages.append(assistant_message)
                    st.rerun()
                except Exception as e:
                    error_message = f"Desculpe, ocorreu um erro: {e}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})