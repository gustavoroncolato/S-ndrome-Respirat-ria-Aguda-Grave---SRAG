import os
from typing import Annotated, List, TypedDict
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv


# Carrega as chaves de API do arquivo .env
load_dotenv()

# Definição do Estado
# O estado é a memória do agente. A chave `messages` irá guardar o histórico da conversa.
# `add_messages` é uma função especial que anexa novas mensagens a esta lista.
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

# Ferramentas
# Define as ferramentas que o agente pode usar. Aqui, usamos a ferramenta de busca da Tavily.
# Esta ferramenta é pré-construída e otimizada para busca em fluxos de agentes.
from langchain_tavily import TavilySearch
tavily_tool = TavilySearch(max_results=3)
tools = [tavily_tool]

# O ToolNode é um nó pré-construído que executa as ferramentas que nosso agente chama.
tool_node = ToolNode(tools)

# Definição do Agente Modelo e Nós
# Inicializa o LLM. Nós vamos vincular (bind) nossas ferramentas a ele para que ele saiba quando e como chamá-las.
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1)
model = model.bind_tools(tools)

# Define o nó do agente. Este é o "cérebro" do nosso agente.
def call_model(state: AgentState):
    """O nó principal para a lógica do agente."""
    messages = state['messages']
    response = model.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState) -> str:
    """
    Esta função atua como um roteador.
    Ela verifica a última mensagem do modelo para ver se ela contém uma chamada de ferramenta.
    """
    last_message = state['messages'][-1]
    # Se não houver chamadas de ferramenta, o agente terminou seu trabalho, e encerra.
    if not last_message.tool_calls:
        return "end"
    # Caso contrário, o agente usa uma ferramenta, então roteamos para o nó de ferramentas.
    else:
        return "continue"

# Montagem do Grafo
# Cria o grafo e define o fluxo de trabalho.
workflow = StateGraph(AgentState)

# Adiciona os nós ao grafo
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

# Define o ponto de entrada para o grafo
workflow.set_entry_point("agent")

# Adiciona a aresta condicional. cria o principal loop de conversação.
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",  # Se o agente chamar uma ferramenta, vai para o nó de ferramentas
        "end": END  # Se o agente terminou, encerra o grafo
    }
)

# Adiciona a aresta que volta das ferramentas para o agente
workflow.add_edge("tools", "agent")

# Compila o grafo em uma aplicação executável
app = workflow.compile()

#Loop de Interação 
if __name__ == "__main__":
    print("Agente pronto. Digite 'sair' ou 'exit' para encerrar a conversa.")
    while True:
        user_input = input("Você: ")
        if user_input.lower() in ["quit", "exit", "sair"]:
            print("Encerrando a conversa.")
            break
        
        # Invoca o grafo com a mensagem do usuário
        # `stream` com a ideia de  obter as respostas à medida que são geradas
        events = app.stream(
            {"messages": [("user", user_input)]},
        )
        
        # printa a resposta final do assistente
        for event in events:
            if "messages" in event:
                event['messages'][-1].pretty_print()