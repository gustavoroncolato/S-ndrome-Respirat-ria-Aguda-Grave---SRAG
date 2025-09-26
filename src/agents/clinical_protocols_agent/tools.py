from langchain.tools import tool
from langchain_tavily import TavilySearch

@tool
def clinical_protocol_search_tool(disease_name: str) -> str:
    """
    Busca informações sobre tratamentos e protocolos clínicos para uma doença respiratória específica
    em fontes médicas confiáveis, como o Ministério da Saúde do Brasil e manuais médicos.
    A entrada deve ser o nome da doença (ex: 'Influenza A').
    """
    print(f"Ferramenta do Sub-Agente: Buscando protocolos para '{disease_name}'")
    
    # Guardrail na query é para garantir a qualidade das fontes
    query = f"protocolo de tratamento ou manejo clínico para '{disease_name}' site:gov.br/saude OR site:msdmanuals.com/pt-br OR site:scielo.br"
    tavily_search = TavilySearch(max_results=3)
    results = tavily_search.invoke(query)
    return results